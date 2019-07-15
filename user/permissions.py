from rest_framework import permissions


class RespondentViewSetPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user
        if user.is_superuser:
            return True

        if view.action == 'create':
            return user.groups.filter(name__in=['budget', 'brigadier', 'coordinator', 'candidate'])
        else:
            return user.groups.filter(name__in=['brigadier', 'coordinator', 'candidate'])


class UserProfileSetPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user

        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return user.has_perms(['user.view_profile'])
        else:
            if view.action in ('update', 'partial_update'):
                return user.has_perm('user.change_profile')
            else:
                return False

    def has_object_permission(self, request, view, obj):

        user = request.user

        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS and user.has_perm('user.view_profile'):
            return obj == user
        elif user.has_perms(['user.change_profile']):
            return obj == user
        else:
            return False


class BudgetViewSetPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return user.has_perm('user.view_budget')
        else:
            if view.action in ['create', 'invite_again']:
                return user.has_perm('user.add_budget')
            if view.action in ['set_firebase_token']:
                return user.is_budget
            elif view.action in ('update', 'partial_update'):
                return user.has_perm('user.change_budget')
            elif view.action == 'destroy':
                return user.has_perm('core.delete_budget')
            else:
                return False

    def has_object_permission(self, request, view, obj):

        user = request.user

        if user.is_superuser:
            return True

        if view.action == 'set_firebase_token' and request.method == 'POST':
            return obj == user

        if request.method in permissions.SAFE_METHODS and user.has_perm('user.view_budget'):
            if user.is_budget:
                return obj == user
            if user.is_brigadier:
                return obj.parent == user
            elif user.is_coordinator:
                return obj.parent == user or obj.parent.parent == user
            elif user.is_candidate:
                return obj.parent == user or obj.parent.parent == user or obj.parent.parent.parent == user
            else:
                return False
        elif user.has_perm('user.change_budget'):
            if user.is_budget:
                return obj == user
            if user.is_brigadier:
                return obj.parent == user
            elif user.is_coordinator:
                return obj.parent == user or obj.parent.parent == user
            elif user.is_candidate:
                return obj.parent == user or obj.parent.parent == user or obj.parent.parent.parent == user
            else:
                return False
        elif user.has_perm('user.delete_budget'):
            if user.is_brigadier:
                return obj.parent == user
            elif user.is_coordinator:
                return obj.parent == user or obj.parent.parent == user
            elif user.is_candidate:
                return obj.parent == user or obj.parent.parent == user or obj.parent.parent.parent == user
            else:
                return False
        else:
            return False


class BrigadierViewSetPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user

        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return user.has_perms(['user.view_brigadier'])
        else:
            if view.action in ['create', 'invite_again']:
                return user.has_perm('user.add_brigadier')
            elif view.action in ('update', 'partial_update'):
                return user.has_perm('user.change_brigadier')
            elif view.action == 'destroy':
                return user.has_perm('core.delete_brigadier')
            else:
                return False

    def has_object_permission(self, request, view, obj):

        user = request.user

        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS and user.has_perm('user.view_brigadier'):
            return obj.parent == user or obj.parent.parent == user or obj == user

        elif user.has_perms(['user.change_brigadier', 'user.delete_brigadier']):
            return obj.parent == user or obj.parent.parent == user
        elif user.has_perms(['user.change_brigadier']):
            return obj == user
        else:
            return False


class CoordinatorViewSetPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user

        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return user.has_perms(['user.view_coordinator'])
        else:
            if view.action in ['create', 'invite_again']:
                return user.has_perm('user.add_coordinator')
            elif view.action in ('update', 'partial_update'):
                return user.has_perm('user.change_coordinator')
            elif view.action == 'destroy':
                return user.has_perm('user.delete_coordinator')
            else:
                return False

    def has_object_permission(self, request, view, obj):

        user = request.user

        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS and user.has_perm('user.view_coordinator'):
            return obj.parent == user or obj == user

        elif user.has_perm('user.add_coordinator'):
            return obj.parent == user
        elif user.has_perms(['user.change_coordinator', 'user.delete_coordinator']):
            return obj.parent == user
        elif user.has_perm('user.change_coordinator'):
            return obj == user
        else:
            return False


class CandidateViewSetPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        user = request.user

        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            if view.action == 'list':
                return False
            return user.has_perms(['user.view_candidate'])
        else:
            if view.action in ('update', 'partial_update'):
                return user.has_perm('user.change_candidate')

        return False

    def has_object_permission(self, request, view, obj):

        user = request.user

        if user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS and user.has_perm('user.view_candidate'):
            return obj == user
        elif user.has_perm('user.change_candidate'):
            return obj == user

        return False
