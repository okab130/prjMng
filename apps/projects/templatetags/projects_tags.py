from django import template

register = template.Library()


@register.filter
def get_status_label(status):
    """ステータスの表示ラベルを取得"""
    status_labels = {
        'PLANNING': '計画中',
        'IN_PROGRESS': '進行中',
        'ON_HOLD': '保留中',
        'COMPLETED': '完了',
        'CANCELLED': 'キャンセル',
    }
    return status_labels.get(status, status)


@register.filter
def get_status_badge_class(status):
    """ステータスのバッジクラスを取得"""
    status_classes = {
        'PLANNING': 'bg-secondary',
        'IN_PROGRESS': 'bg-primary',
        'ON_HOLD': 'bg-warning',
        'COMPLETED': 'bg-success',
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
