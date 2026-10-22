ROLE_RANK = {
    "owner": 3,
    "admin": 2,
    "manager": 2,
    "member": 1,
}


def get_workspace_membership(user, workspace):
    if not getattr(user, "is_authenticated", False):
        return None

    return workspace.memberships.enabled().filter(user=user).first()


def get_workspace_role(user, workspace):
    if getattr(user, "is_authenticated", False) and workspace.owner_id == user.pk:
        return "owner"

    membership = get_workspace_membership(user, workspace)
    if membership is None:
        return None
    return membership.role


def has_workspace_role(user, workspace, minimum_role):
    role = get_workspace_role(user, workspace)
    if role is None:
        return False
    return ROLE_RANK[role] >= ROLE_RANK[minimum_role]
