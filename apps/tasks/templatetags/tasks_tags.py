from django import template

register = template.Library()


@register.filter
def get_status_label(status):
    """タスクステータスの表示ラベルを取得"""
    status_labels = {
        'NOT_STARTED': '未着手',
        'IN_PROGRESS': '進行中',
        'COMPLETED': '完了',
        'ON_HOLD': '保留',
        'CANCELLED': 'キャンセル',
    }
    return status_labels.get(status, status)


@register.filter
def get_status_badge_class(status):
    """タスクステータスのバッジクラスを取得"""
    status_classes = {
        'NOT_STARTED': 'bg-secondary',
        'IN_PROGRESS': 'bg-primary',
        'COMPLETED': 'bg-success',
        'ON_HOLD': 'bg-warning',
        'CANCELLED': 'bg-danger',
    }
    return status_classes.get(status, 'bg-secondary')


@register.filter
def get_priority_label(priority):
    """優先度の表示ラベルを取得"""
    priority_labels = {
        'LOW': '低',
        'MEDIUM': '中',
        'HIGH': '高',
        'URGENT': '緊急',
    }
    return priority_labels.get(priority, priority)


@register.filter
def get_priority_badge_class(priority):
    """優先度のバッジクラスを取得"""
    priority_classes = {
        'LOW': 'bg-info',
        'MEDIUM': 'bg-primary',
        'HIGH': 'bg-warning',
        'URGENT': 'bg-danger',
    }
    return priority_classes.get(priority, 'bg-secondary')
