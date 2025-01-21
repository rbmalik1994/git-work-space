from manim import *
import git, sys, numpy

class GitStory(MovingCameraScene):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.drawn_commits = {}
        self.commit_list = []
        self.commit_children = {}
        self.child_chain_length = 0
        self.zoom_out_count = 0

        # Set font color based on light mode
        self.font_color = BLACK if self.args.light_mode else WHITE

    def measure_child_chain_length(self, commit):
        try:
            if len(self.commit_children[commit.hexsha]) > 0:
                for child in self.commit_children[commit.hexsha]:
                    self.child_chain_length += 1
                    return self.measure_child_chain_length(child)
            else:
                return self.child_chain_length
        except KeyError:
            return self.child_chain_length

    def construct(self):
        # Try to find the Git repository
        try:
            self.repo = git.Repo(search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError:
            print("git-story error: No Git repository found at current path.")
            sys.exit(1)
        
        # Try to get the list of commits
        try:
            self.commit_list = list(self.repo.iter_commits(self.args.commit_id))[:self.args.commits]
        except git.exc.GitCommandError:
            print("git-story error: No commits in current Git repository.")
            sys.exit(1)

        # Adjust the number of commits if necessary
        if len(self.commit_list) < self.args.commits:
            self.args.commits = len(self.commit_list)

        # Reverse the commits if not in reverse mode
        if not self.args.reverse:
            self.commit_list.reverse()
            for commit in self.commit_list:
                if len(commit.parents) > 0:
                    for parent in commit.parents:
                        self.commit_children.setdefault(parent.hexsha, []).append(commit)
            z = 1
            while self.measure_child_chain_length(self.commit_list[0]) < self.args.commits - 1:
                self.commit_list = list(self.repo.iter_commits(self.args.commit_id))[:self.args.commits + z]
                self.commit_list.reverse()
                self.commit_children = {}
                for commit in self.commit_list:
                    if len(commit.parents) > 0:
                        for parent in commit.parents:
                            self.commit_children.setdefault(parent.hexsha, []).append(commit)
                z += 1

            # Invert branches if necessary
            if self.args.invert_branches:
                for parent in self.commit_children:
                    if len(self.commit_children[parent]) > 1:
                        self.commit_children[parent].reverse()

        commit = self.commit_list[0]

        # Load the logo image
        logo = ImageMobject(self.args.logo)
        logo.width = 3

        # Show intro if enabled
        if self.args.show_intro:
            self.add(logo)

            intro_text = Text(self.args.title, font="Monospace", font_size=36, color=self.font_color).to_edge(UP, buff=1)
            self.add(intro_text)
            self.wait(2)
            self.play(FadeOut(intro_text))
            self.play(logo.animate.scale(0.25).to_edge(UP, buff=0).to_edge(RIGHT, buff=0))
    
            self.camera.frame.save_state()
            self.play(FadeOut(logo))

        else:
            logo.scale(0.25).to_edge(UP, buff=0).to_edge(RIGHT, buff=0)
            self.camera.frame.save_state()

        i = 0
        previous_circle = None
        elements_to_fade_out = Group()
        self.parse_commits(commit, i, previous_circle, elements_to_fade_out)

        # Adjust camera frame to fit the commits
        self.play(self.camera.frame.animate.move_to(elements_to_fade_out.get_center()), run_time=1/self.args.speed)
        self.play(self.camera.frame.animate.scale_to_fit_width(elements_to_fade_out.get_width() * 1.1), run_time=1/self.args.speed)

        if elements_to_fade_out.get_height() >= self.camera.frame.get_height():
            self.play(self.camera.frame.animate.scale_to_fit_height(elements_to_fade_out.get_height() * 1.25), run_time=1/self.args.speed)

        self.wait(3)

        self.play(FadeOut(elements_to_fade_out), run_time=1/self.args.speed)

        # Show outro if enabled
        if self.args.show_outro:
            self.play(Restore(self.camera.frame))
            self.play(logo.animate.scale(4).set_x(0).set_y(0))

            outro_top_text = Text(self.args.outro_top_text, font="Monospace", font_size=36, color=self.font_color).to_edge(UP, buff=1)
            self.play(AddTextLetterByLetter(outro_top_text))

            outro_bottom_text = Text(self.args.outro_bottom_text, font="Monospace", font_size=36, color=self.font_color).to_edge(DOWN, buff=1)
            self.play(AddTextLetterByLetter(outro_bottom_text))

            self.wait(3)

    def parse_commits(self, commit, index, previous_circle, elements_to_fade_out):
        if index < self.args.commits and commit in self.commit_list:
            # Determine the fill color of the commit circle
            commit_fill_color = RED if len(commit.parents) <= 1 else GRAY

            circle = Circle(stroke_color=commit_fill_color, fill_color=commit_fill_color, fill_opacity=0.25)
            circle.height = 1

            if previous_circle:
                circle.next_to(previous_circle, RIGHT, buff=1.5)

            offset = 0
            while any((circle.get_center() == c).all() for c in self.get_commit_centers()):
                circle.next_to(circle, DOWN, buff=3.5)
                offset += 1
                if self.zoom_out_count == 0:
                    self.play(self.camera.frame.animate.scale(1.5), run_time=1/self.args.speed)
                self.zoom_out_count += 1

            is_new_commit = commit.hexsha not in self.drawn_commits

            # Determine the start and end points for the arrow
            if not self.args.reverse:
                if is_new_commit:
                    start = circle.get_center()
                    end = previous_circle.get_center() if previous_circle else LEFT
                else:
                    start = self.drawn_commits[commit.hexsha].get_center()
                    end = previous_circle.get_center()
            else:
                if is_new_commit:
                    start = previous_circle.get_center() if previous_circle else LEFT
                    end = circle.get_center()
                else:
                    start = previous_circle.get_center()
                    end = self.drawn_commits[commit.hexsha].get_center()

            arrow = Arrow(start, end, color=self.font_color)
            length = numpy.linalg.norm(start - end) - (1.5 if start[1] == end[1] else 3)
            arrow.set_length(length)

            angle = arrow.get_angle()
            line_rect = Rectangle(height=0.1, width=length, color="#123456").move_to(arrow.get_center()).rotate(angle)

            for commit_circle in self.drawn_commits.values():
                intersection = Intersection(line_rect, commit_circle)
                if intersection.has_points():
                    arrow = CurvedArrow(start, end)
                    if start[1] == end[1]:
                        arrow.shift(UP * 1.25)
                    if start[0] < end[0] and start[1] == end[1]:
                        arrow.flip(RIGHT).shift(UP)
                
            commit_id_text = Text(commit.hexsha[0:6], font="Monospace", font_size=20, color=self.font_color).next_to(circle, UP)

            commit_message = commit.message[:40].replace("\n", " ")
            message_text = Text('\n'.join(commit_message[j:j+20] for j in range(0, len(commit_message), 20))[:100], font="Monospace", font_size=14, color=self.font_color).next_to(circle, DOWN)

            if is_new_commit:
                self.play(self.camera.frame.animate.move_to(circle.get_center()), Create(circle), AddTextLetterByLetter(commit_id_text), AddTextLetterByLetter(message_text), run_time=1/self.args.speed)
                self.drawn_commits[commit.hexsha] = circle

                previous_ref = commit_id_text
                if commit.hexsha == self.repo.head.commit.hexsha:
                    head_rect = Rectangle(color=BLUE, fill_color=BLUE, fill_opacity=0.25, width=1, height=0.4)
                    head_rect.next_to(commit_id_text, UP)
                    head_text = Text("HEAD", font="Monospace", font_size=20, color=self.font_color).move_to(head_rect.get_center())
                    self.play(Create(head_rect), Create(head_text), run_time=1/self.args.speed)
                    elements_to_fade_out.add(head_rect, head_text)
                    previous_ref = head_rect

                branch_count = 0
                for branch in self.repo.heads:
                    if commit.hexsha == branch.commit.hexsha:
                        branch_text = Text(branch.name, font="Monospace", font_size=20, color=self.font_color)
                        branch_rect = Rectangle(color=GREEN, fill_color=GREEN, fill_opacity=0.25, height=0.4, width=branch_text.width + 0.25)

                        branch_rect.next_to(previous_ref, UP)
                        branch_text.move_to(branch_rect.get_center())

                        previous_ref = branch_rect 

                        self.play(Create(branch_rect), Create(branch_text), run_time=1/self.args.speed)
                        elements_to_fade_out.add(branch_rect, branch_text)

                        branch_count += 1
                        if branch_count >= self.args.max_branches_per_commit:
                            break

                tag_count = 0
                for tag in self.repo.tags:
                    if commit.hexsha == tag.commit.hexsha:
                        tag_text = Text(tag.name, font="Monospace", font_size=20, color=self.font_color)
                        tag_rect = Rectangle(color=YELLOW, fill_color=YELLOW, fill_opacity=0.25, height=0.4, width=tag_text.width + 0.25)

                        tag_rect.next_to(previous_ref, UP)
                        tag_text.move_to(tag_rect.get_center())

                        previous_ref = tag_rect

                        self.play(Create(tag_rect), Create(tag_text), run_time=1/self.args.speed)
                        elements_to_fade_out.add(tag_rect, tag_text)

                        tag_count += 1
                        if tag_count >= self.args.max_tags_per_commit:
                            break

            else:
                self.play(self.camera.frame.animate.move_to(self.drawn_commits[commit.hexsha].get_center()), run_time=1/self.args.speed)
                self.play(Create(arrow), run_time=1/self.args.speed)
                elements_to_fade_out.add(arrow)
                return

            if previous_circle:
                self.play(Create(arrow), run_time=1/self.args.speed)
                elements_to_fade_out.add(arrow)

            previous_circle = circle

            elements_to_fade_out.add(circle, commit_id_text, message_text)

            # Parse the commit parents or children based on the reverse flag
            if self.args.reverse:
                commit_parents = list(commit.parents)
                if len(commit_parents) > 0:
                    if self.args.invert_branches:
                        commit_parents.reverse()

                    if self.args.hide_merged_chains:
                        self.parse_commits(commit_parents[0], index + 1, previous_circle, elements_to_fade_out)
                    else:
                        for parent in commit_parents:
                            self.parse_commits(parent, index + 1, previous_circle, elements_to_fade_out)
            else:
                try:
                    if len(self.commit_children[commit.hexsha]) > 0:
                        if self.args.hide_merged_chains:
                            self.parse_commits(self.commit_children[commit.hexsha][0], index + 1, previous_circle, elements_to_fade_out)
                        else:
                            for child in self.commit_children[commit.hexsha]:
                                self.parse_commits(child, index + 1, previous_circle, elements_to_fade_out)
                except KeyError:
                    pass
        else:
            return

    def get_commit_centers(self):
        return [commit.get_center() for commit in self.drawn_commits.values()]