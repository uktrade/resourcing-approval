from main.models import Approval


USERNAME_APPROVAL_ORDER = [
    ("head-of-profession", Approval.Type.HEAD_OF_PROFESSION),
    ("chief", Approval.Type.CHIEF),
    ("busops", Approval.Type.BUSOPS),
    ("hrbp", Approval.Type.HRBP),
    ("finance", Approval.Type.FINANCE),
    ("commercial", Approval.Type.COMMERCIAL),
    ("director", Approval.Type.DIRECTOR),
    ("dg-coo", Approval.Type.DG_COO),
]
