"""
Page guides for the Wagtail admin.

A guide explains what an edit page is for and how to fill it in, beyond
what fits in a field help text. It is shown at the top of the form as a
short summary plus a "Full guide" button that opens a modal dialog.

Usage in a panel list::

    panels = [GuidePanel(MY_GUIDE), FieldPanel("name"), ...]

All strings are lazy (gettext_lazy) so the guide follows the admin language.
"""

from dataclasses import dataclass, field

from wagtail.admin.panels import HelpPanel


@dataclass(frozen=True)
class GuideSection:
    title: str
    paragraphs: tuple = ()
    steps: tuple = ()


@dataclass(frozen=True)
class AdminGuide:
    key: str
    title: str
    summary: str
    sections: tuple = field(default_factory=tuple)


class GuidePanel(HelpPanel):
    def __init__(self, guide, **kwargs):
        kwargs.setdefault("template", "admin/guide_panel.html")
        super().__init__(**kwargs)
        self.guide = guide

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs["guide"] = self.guide
        return kwargs

    class BoundPanel(HelpPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.guide = self.panel.guide
