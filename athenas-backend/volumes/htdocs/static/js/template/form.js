{% spaceless %}
{% autoescape on %}{% load filters %}
{% if tabs %}
new Ext.TabPanel({
    border: false,
    activeTab: 0,
    autoWidth: true,
    frame: true,
    items: [
        {% for tab in tabs %}
        {
            xtype: "panel",
            border: false,
            autoHeight: true,
            title: "{{ tab.title }}",
            style: "padding: 1em",
            layoutOnTabChange: true,
            {% if tab.layout %}
                layout: "{{ tab.layout }}",
                border: false,
                layoutConfig: { columns: "{{ tab.column }}" },
                items: [
                    {% for field in tab.field %}
                    {
                        xtype: "panel",
                        width: 475 / {{ tab.column }},
                        layout: "form",
                        border: false,
                        style: "margin-right: 2pt",
                        labelAlign: "right",
                        items: [{ {{ form|toExtField:field|safe }} }]
                    },
                    {% endfor %}
                ]
            {% else %}
                layout: "form",
                defaults: {
                    width: 370
                },
                labelWidth: 105,
                items: [{% for field in tab.field %}
                    {% if forloop.last %}{ {{ form|toExtField:field|safe }} }{% else %}{ {{ form|toExtField:field|safe }} },{% endif %}
                {% endfor %}]
            {% endif %}
        },
        {% endfor %}
    ]
})
{% else %}
new Ext.Panel({
    border: false,
    autoHeight: true,
    layout: "form",
    style: "padding: 1em",
    defaults: {
        width: 370
    },
    labelWidth: 105,
    items: [{% for field in form %}
        {% if forloop.last %}{ {{ form|toExtField:field|safe }} }{% else %}{ {{ form|toExtField:field|safe }} },{% endif %}
    {% endfor %}]
})
{% endif %}
{% endautoescape %}
{% endspaceless %}