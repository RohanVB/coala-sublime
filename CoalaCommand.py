import sublime_plugin
import sublime
import json
from .coalaThread import coalaThread
from .Utils import log, COALA_KEY


def show_output(view):
    output_str = view.settings().get(COALA_KEY + ".output_str")
    if not output_str:
        return
    output = json.loads(output_str)

    region_flag = sublime.DRAW_OUTLINED
    regions = []

    for section_name, section_results in output["results"].items():
        for result in section_results:
            if not result["affected_code"]:
                continue
            for code_region in result["affected_code"]:
                line = view.line(
                    view.text_point(code_region["start"]["line"]-1, 0))
                regions.append(line)

    view.add_regions(COALA_KEY, regions, COALA_KEY, "dot", region_flag)


class coalaCommand(sublime_plugin.TextCommand):
    """
    The coalaCommand inherits the TextCommand from sublime_plugin and can be
    executed using `view.run_command("coala")` - which executes the `run()`
    function by default.
    """

    def run(self, edit, **kwargs):
        file_name = self.view.file_name()
        log("Trying to run coala on", file_name)
        if file_name:
            thread = coalaThread(self.view, show_output)
            thread.start()
            self.progress_tracker(thread)
        else:
            sublime.status_message("Save the file to run coala on it")

    def progress_tracker(self, thread, i=0):
        """ Display spinner while coala is running """
        icons = [u"◐", u"◓", u"◑", u"◒"]
        sublime.status_message("Running coala %s" % icons[i])
        if thread and thread.is_alive():
            i = (i + 1) % 4
            sublime.set_timeout(lambda: self.progress_tracker(thread, i), 100)
        else:
            sublime.status_message("")
