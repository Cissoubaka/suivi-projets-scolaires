"""Package des onglets de l'application"""

from tabs.projects_tab import ProjectsTab
from tabs.students_tab import StudentsTab
from tabs.groups_tab import GroupsTab
from tabs.rating_tab import RatingTab
from tabs.task_assignment_tab import TaskAssignmentTab
from tabs.attendance_tab import AttendanceTab
from tabs.export_tab import ExportTab

__all__ = [
    'ProjectsTab', 'StudentsTab', 'GroupsTab', 'RatingTab',
    'TaskAssignmentTab', 'AttendanceTab', 'ExportTab'
]


