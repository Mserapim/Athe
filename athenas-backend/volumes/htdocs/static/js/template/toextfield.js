{% autoescape on %}
name: "{{ name }}",
fieldLabel: "{{ label|safe }}",
xtype: "{{ xtype|safe }}"
{% if types %},
types: {{ types|safe }}
{% endif %}
{% if value %},
    value: {{ value|safe }}
{% endif %}
{% if autoHeight %},
    autoHeight: {{ autoHeight }}
{% endif %}
{% if height %},
    height: {{ height }}
{% endif %}
{% if allowBlank %},
    allowBlank: {{ allowBlank }},
    validateOnBlur: true,
    blankText: "É necessário preencher este campo."
{% endif %}
{% if checked %}, checked: {{ checked|safe }}{% endif %}
{% if cls %}, cls: "{{ cls }}"{% endif %}
{% if store %},
    store: {{ store|safe }},
    tpl: {{ tpl|safe }},
    displayField: 'description',
    valueField: 'id',
    itemSelector: 'div.search-item'
    {% if controller %}, controller: "{{ controller }}"{% endif %}
{% endif %}
{% if storeSimple %},
    store: {{ storeSimple|safe }},
    displayField: 'description',
    typeAhead: true,
    mode: "local",
    triggerAction: 'all',
    emptyText:'Selecione um item...',
    selectOnFocus:true,
    editable: true,
    resizable: true
{% endif %}
{% if model %},
    model: {
        name: "{{ model }}",
        pkg: "{{ package }}"
    },
    controller: "{{ controller }}",
    queryset: {{ queryset|safe }}
{% endif %}
{% endautoescape %}