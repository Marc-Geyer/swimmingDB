from django.db.models import QuerySet, Model


def get_entries(model: type[Model], filter, order_by):
    entries: QuerySet
    if filter:
        entries = model.objects.filter(**filter)
    else:
        entries = model.objects.all()

    if order_by:
        if isinstance(order_by, str):
            entries = entries.order_by(order_by)
        elif isinstance(order_by, list):
            entries = entries.order_by(*order_by)

    return entries