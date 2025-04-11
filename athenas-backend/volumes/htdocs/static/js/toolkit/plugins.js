if (typeof(toolkit) == "undefiend") {
} else {

    toolkit.plugins = {
        DEBUG_MODE: true
    }

    toolkit.plugins.JsonGridPanel = Ext.extend(
        Ext.grid.GridPanel,
        {
            getFindFields: function(cf) {
                var fields = []

                Ext.each(
                        cf.toSearch,
                        function(item) {
                            fields.push(new Ext.menu.CheckItem({
                                text: item.header,
                                dataIndex: item.dataIndex,
                                checked: true,
                                listeners: {
                                    scope: this,
                                    checkchange: function() {
                                        this.setFilter();
                                    }
                                }
                            }));
                        },
                        this
                        );

                return fields;
            },

            setFilter: function() {
                var store = this.getStore();
                var fields = [];

                if (this.fieldsToSearch.menu)
                    this.fieldsToSearch.menu.items.each(
                            function(item) {
                                if (item.checked)
                                    fields.push(item.dataIndex);
                            }
                            );

                var keyword = this.findText.getValue();

                if (keyword != undefined && keyword != '') {
                    store.baseParams.keyword = keyword;
                    if (fields.length > 0) store.baseParams.toSearch = fields;
                }
                else {
                    store.baseParams.keyword = undefined;
                    store.baseParams.toSearch = undefined;
                }

                store.reload({params: {start: 0}});
            },

            getToolbar: function(cf) {
                if (!this.toolbar) {

                    this.findText = new Ext.form.TextField({
                        width: 300,
                        enableKeyEvents: true,
                        emptyText: 'Informe o texto a ser pesquisado e clique em Localizar.',
                        listeners: {
                            scope: this,
                            keypress: function(text, event) {
                                if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                                    this.setFilter();
                                }
                            }
                        }
                    });

                    var fields = this.getFindFields(cf);

                    if (fields.length > 0)
                        this.fieldsToSearch = new Ext.Button({
                            text: 'Localizar por : ',
                            menu: fields
                        });
                    else
                        this.fieldsToSearch = new Ext.form.Label({
                            text: 'Localizar por : '
                        });


                    this.toolbar = new Ext.Toolbar({
                        items: [
                            ' ',
                            this.fieldsToSearch,
                            ' ',
                            ' ',
                            this.findText,
                            ' ',
                            ' ',
                            {
                                xtype: 'button',
                                text: 'Localizar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/find.png',
                                handler: this.setFilter,
                                scope: this
                            },
                            ' ',
                            {
                                xtype: 'button',
                                text: 'Limpar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/clean.png',
                                handler: function() {
                                    this.findText.setValue('');
                                    this.setFilter();
                                    this.findText.getEl().dom.focus();
                                },
                                scope: this
                            }
                        ]
                    });
                }

                return this.toolbar;
            },

            constructor: function(cf) {
                if(cf.store) {
                   cf.store.baseParams.limit = 50;
                   if(cf.store.autoLoad == null || cf.store.autoLoad == true) {
                        cf.store.load({
                            params: {
                                start: 0
                            }
                        });
                   }
               }
               else {
                    throw 'O store não foi definido.'
               }

                if (cf.searchable) cf.tbar = this.getToolbar(cf);

                if (cf.store.url)
                    cf.controller = cf.store.url.split('/')[2];
                else if(cf.store.proxy && cf.store.proxy.api.read)
                    cf.controller = cf.store.proxy.api.read.url.split('/')[2];

                this.paginator = new Ext.PagingToolbar({
                    store: cf.store,
                    displayInfo: true,
                    pageSize: 50
                });

                cf.bbar = this.paginator;

                toolkit.plugins.JsonGridPanel.superclass.constructor.call(this, cf);

                this.on({
                    scope: this,
                    render: function() {
                        new Ext.LoadMask(
                            this.ownerCt.getEl(),
                            {
                                msg: 'Estamos trabalhando na sua solicitação.',
                                store: cf.store
                            }
                        ).show();
                    }
                });
            }
        }
    );

    Ext.reg("json-grid", toolkit.plugins.JsonGridPanel);

    toolkit.plugins.AutocompleteSelectWindow = Ext.extend(
        Ext.Window,
        {
            send: function() {
                var rec = this.grid.getSelectionModel().getSelected();
                if (rec) {
                    var father = this.father;

                    father.setValue(rec.get("id"));
                    father.focus();

                    this.destroy();
                }
                else {
                    alert("Selecione um item primeiro, ou cancele esta seleção.");
                }
            },

            constructor: function(father) {

                this.father = father;

                this.grid = new toolkit.plugins.JsonGridPanel({
                    controller: father.crudController,
                    searchable: true,
                    height: 375,
                    toSearch: [],
                    cm: new Ext.grid.ColumnModel(
                            toolkit.util.Ajax.request_json(
                                "POST",
                                toolkit.util.Normalize.controller_action(
                                        this.father.crudController,
                                        "get_columns_grid"
                                    )
                                )
                            ),
                    store: new Ext.data.JsonStore({
                        fields: toolkit.util.Ajax.request_json(
                            "POST",
                            toolkit.util.Normalize.controller_action(
                                this.father.crudController,
                                "get_field_list"
                            )
                        ),
                        url: toolkit.util.Normalize.controller_action(
                            this.father.crudController,
                            this.father.queryAction
                        ),
                        root: "result",
                        totalProperty: "totalRows",
                        listeners: {
                            scope: this,
                            load: function(store) {
                                try {
                                    var id = this.father.hiddenField.value;
                                    this.grid.getSelectionModel().selectRow(store.find("id", id));
                                }
                                catch(e) {}
                            }
                        }
                    }),
                    sm: new Ext.grid.RowSelectionModel({
                        singleSelect: true
                    })
                });

                var cfg = {
                    title: "Selecione (" +
                    toolkit.util.Ajax.request_json(
                        "POST",
                        toolkit.util.Normalize.controller_action(
                            this.father.crudController,
                            "get_title",
                            ["PANEL",]
                        )
                    ).title + ")",
                    closable: true,
                    border: false,
                    layout: "fit",
                    width: 550,
                    modal: true,
                    buttonAlign: "center",
                    items: [this.grid],
                    buttons: [
                        {
                            text: "Selecionar",
                            scope: this,
                            handler: function() {
                                this.send();
                            }
                        },
                        {
                            text: "Cancelar",
                            scope: this,
                            handler: function() {
                                this.destroy();
                            }
                        }
                    ]
                }

                toolkit.plugins.AutocompleteSelectWindow.superclass.constructor.call(this, cfg);
            }
        }
    );

    toolkit.plugins.AutocompleteField = Ext.extend(
        Ext.form.ComboBox,
        {
            _select: function() {
                var frm = new toolkit.plugins.AutocompleteSelectWindow(this);
                frm.show();
            },

            setReadOnly: function(readOnly) {
                if(!readOnly) this.actionButtons.enable();
                else this.actionButtons.disable();

                toolkit.plugins.AutocompleteField.superclass.setReadOnly.call(this, readOnly);
            },

            __setValueCallback: function() {
                var store = this.getStore();
                store.proxy.setUrl(this.getStore().proxy.oldUrl);
                this.getStore().proxy.oldUrl = undefined;

                if(store.getCount() > 0) {
                    value = store.getAt(0).get(this.valueField);
                    toolkit.plugins.AutocompleteField.superclass.setValue.call(this, value);
                }

                store.un('load', this.__setValueCallback, this);
            },

            setValue: function(value) {
                var store = this.getStore();
                try {
                    store.proxy.oldUrl = store.proxy.url;

                    if(Ext.isArray(value)) value = value[1];

                    if(store.find(this.valueField, value) < 0 && !Ext.isEmpty(value)) {
                        store.proxy.setUrl(toolkit.util.Normalize.controller_action(this.controller, 'get'));
                        store.on('load', this.__setValueCallback, this);
                        store.load({params: {pk: value}});
                    }
                    else if(!Ext.isEmpty(value)) {
                        toolkit.plugins.AutocompleteField.superclass.setValue.call(this, value);
                    }
                }
                catch(e) {console.warn(e)}
            },

            _edit: function() {

                if (this.controller instanceof Array) {
                    console.warn('A funcionalidade de herança ainda não foi completada, favor remover este uso.');
                    alert('Foi encontrato um bug. Contacte a equipe de desenvolvimento.');
                    return;
                }

                if (this.hiddenField.value != undefined && this.hiddenField.value != "") {
                    var scope = {
                        father : {
                            controller: this.controller,
                            id: "tbm",
                            reload_grid: function() {
                            }
                        },
                        form: false
                    };

                    scope.form = new toolkit.widget.ExtCrudForm(scope.father, 2, this.hiddenField.value);
                    scope.form.action_commit_ex = scope.form.action_commit;
                    scope.form.el = this;
                    scope.form.action_commit = function(type) {
                        var r = this.action_commit_ex(type);

                        this.el.setValue(r.cid);

                        return r;
                    }

                    scope.form.show();
                }
                else
                    console.debug("nenhum item foi selecionado");
            },

            constructor: function(cf) {
                if (cf.name) {
                    cf.hiddenName = cf.name;
                    cf.name = undefined;
                }

                cf.hideTrigger = true;
                cf.minChars = 3;
                cf.triggerAction = 'all'

                cf.width -= 45;

                if (cf.value instanceof Array && cf.value[1] != undefined) {
                    cf.hiddenValue = cf.value[1];
                }
                else {
                    cf.hiddenValue = "";
                }

                if (cf.conf == undefined)
                    cf.conf = {
                        canAdd: true,
                        canEdit: true
                    }
                else {
                    cf.conf.canAdd = cf.conf.canAdd == undefined ? true : cf.conf.canAdd;
                    cf.conf.canEdit = cf.conf.canEdit == undefined ? true : cf.conf.canEdit;
                }

                toolkit.plugins.AutocompleteField.superclass.constructor.call(this, cf);

                this.setValue(cf.hiddenValue);
            },

            onRender: function(container, position) {
                var input = new Ext.Panel({
                    border: false
                });

                var bnts = [];
                var flag = true;

                bnts.push({
                    text: "Limpar",
                    scope: this,
                    iconCls: true,
                    handler: this._clear,
                    icon: "/" + global.Context + "/static/images/edit-clear-locationbar-rtl.png"
                });

                if (this.conf.canAdd) {
                    if (flag) bnts.push('-');
                    flag = false;

                    if (this.controller instanceof Array) {
                        var menu = [];

                        console.debug(this.controller);

                        Ext.each(
                                this.controller,
                                function(ctl) {
                                    menu.push({
                                        text: ctl.title,
                                        scope: this,
                                        handler: function() {
                                            this._new(ctl.controller);
                                        }
                                    });
                                },
                                this
                                );

                        bnts.push({
                            disabled: (this.controller == undefined ? true : false),
                            text: "Adicionar",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/appointment-new.png",
                            menu: menu
                        });
                    }
                    else {
                        bnts.push({
                            disabled: (this.controller == undefined ? true : false),
                            text: "Adicionar",
                            handler: function() {
                                this._new(this.controller)
                            },
                            scope: this,
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/appointment-new.png"
                        })
                    }
                }

                if (this.conf.canEdit) {
                    if (flag) bnts.push('-');
                    flag = false;
                    bnts.push({
                        disabled: (this.controller == undefined ? true : false),
                        text: "Editar",
                        handler: this._edit,
                        scope: this,
                        iconCls: true,
                        icon: "/" + global.Context + "/static/images/edit.png"
                    })
                }

                bnts.push('-');
                bnts.push({
                    disabled: (this.controller == undefined ? true : false),
                    text: "Selecionar",
                    handler: this._select,
                    scope: this,
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/document-export.png"
                });

                this.actionButtons = new Ext.Button({
                    xtype: "button",
                    style: "margin: 0 0 0 5pt",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/view-sort-ascending.png",
                    menu: bnts
                });

                new Ext.Panel({
                    renderTo: container,
                    border: false,
                    layout: "table",
                    items: [
                        input,
                        {
                            xtype: "panel",
                            border: false,
                            items: [ this.actionButtons ]
                        }
                    ]
                });

                toolkit.plugins.AutocompleteField.superclass.onRender.call(this, input.body);
            },

            _clear: function() {
                this.setValue("");
            },

            _new: function(controller) {
                var scope = {
                    father : {
                        controller: controller,
                        id: "tbm",
                        reload_grid: function() {
                        }
                    },
                    form: false
                };

                scope.form = new toolkit.widget.ExtCrudForm(scope.father, 1);
                scope.form.action_commit_ex = scope.form.action_commit;
                scope.form.el = this;
                scope.form.action_commit = function(type) {
                    var r = this.action_commit_ex(type);

                    this.el.setValue(r.cid);

                    return r;
                }

                scope.form.show();
            }
        }
    );

    Ext.reg("autocomplete", toolkit.plugins.AutocompleteField);

    toolkit.plugins.ComboBoxField = Ext.extend(
        Ext.form.ComboBox,
        {
            constructor: function(cf) {
                if (cf.value instanceof Array) {
                    cf.pkValue = cf.value[1];
                    cf.value = cf.value[0];

                    if (cf.pkValue == null) {
                        cf.pkValue = ""
                        cf.value = undefined;
                    }
                }
                else if (cf.value != "") {
                    cf.pkValue = cf.value;
                }
                else {
                    cf.pkValue = ""
                    cf.value = undefined;
                }

                toolkit.plugins.ComboBoxField.superclass.constructor.call(this, cf);
            },

            onRender: function(container, position) {
                var el;
                var data = {
                    name: this.name,
                    value: this.pkValue
                }

                var tpl = new Ext.XTemplate('<input type="hidden" name="{name}" value="{value}"/>');

                if (position)
                    el = tpl.insertBefore(position, data, true);
                else
                    el = tpl.append(container, data, true);

                toolkit.plugins.ComboBoxField.superclass.onRender.call(this, container, position);
                this.input = el.dom;

                try {
                    var index = this.store.find("id", this.pkValue);
                    var record = this.store.getAt(index);
                    this.value = record.data.description;
                }
                catch(e) {
                    this.value = undefined;
                    this.pkValue = "";
                }

                this.el.dom.name = "";

                this.on("select", function(cmb, rec, idx) {
                    this.input.value = rec.data.id;
                })
            },

            getValue: function() {
                if (this.pkValue && this.pkValue != "")
                    return this.pkValue;
                else
                    return "";
            }
        }
    );


    /**
     * Registando na ExtJS, isto cria um novo xtype "combobox"
     */
    Ext.reg("combobox", toolkit.plugins.ComboBoxField);

    toolkit.plugins.ModelMultipleSelectForm = Ext.extend(
        Ext.Window,
        {
            send: function() {
                var sels = this.grid.getSelectionModel().getSelections();
                var opt;

                for (var idx in sels) {
                    var rec = sels[idx];
                    if (typeof(rec) != "function") {
                        this.father.store.add(rec);

                        opt = document.createElement("option");
                        opt.value = rec.data['pk'];
                        opt.appendChild(document.createTextNode(rec.data['description']));
                        opt.selected = true;

                        this.father.el.appendChild(opt);
                    }

                }

                this.destroy();
            },

            constructor: function(model, pkg, father) {
                var qs = [];

                for (var idx in father.queryset) {
                    var row = father.queryset[idx];

                    if (typeof(row) != "function") {
                        if (father.store.find("pk", row.pk) < 0)
                            qs.push(row);
                    }
                }

                var store = new Ext.data.JsonStore({
                    fields: ["pk", "description", "status"],
                    url: toolkit.util.Normalize.controller_action(
                        father.controller,
                        "query"
                    ),
                    baseParams: {
                        pkg: pkg,
                        model: model
                    },
                    root: "result",
                    totalProperty: "totalRows"
                });

                this.father = father;

                this.selModel = new Ext.grid.CheckboxSelectionModel();

                this.grid = new toolkit.plugins.JsonGridPanel({
                    store: store,
                    border: false,
                    searchable: true,
                    toSearch: [],
                    cm: new Ext.grid.ColumnModel([
                        this.selModel,
                        {
                            header: "Chave",
                            dataIndex: "pk",
                            width: 45,
                            sortable: true
                        },

                        {
                            header: "Descrição",
                            dataIndex: "description",
                            sortable: true,
                            width: 550 - 105
                        }
                    ]),
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: 'Selecionar',
                            handler: this.send,
                            scope: this
                        },
                        {
                            text: 'Cancelar',
                            handler: function() {
                                this.destroy();
                            },
                            scope: this
                        }
                    ]
                });

                var cf = {
                    title: "Seletor de itens",
                    layout: "fit",
                    width: 550,
                    height: 325,
                    modal: true,
                    items: [
                        this.grid
                    ]
                };

                toolkit.plugins.ModelMultipleSelectForm.superclass.constructor.call(this, cf);
            }
        }
    );

    toolkit.plugins.ModelMultipleSelectFormCustom = Ext.extend(
        toolkit.plugins.ModelMultipleSelectForm,
        {
            constructor: function(model, pkg, father, method) {
                var qs = [];

                for (var idx in father.queryset) {
                    var row = father.queryset[idx];

                    if (typeof(row) != "function") {
                        if (father.store.find("pk", row.pk) < 0)
                            qs.push(row);
                    }
                }

                var store = new Ext.data.JsonStore({
                    fields: ["pk", "description", "status"],
                    url: toolkit.util.Normalize.controller_action(
                            father.controller,
                            method
                            ),
                    baseParams: {
                        pkg: pkg,
                        model: model
                    },
                    root: "result",
                    totalProperty: "totalRows"
                });

                this.father = father;

                this.selModel = new Ext.grid.CheckboxSelectionModel();

                this.grid = new toolkit.plugins.JsonGridPanel({
                    store: store,
                    border: false,
                    searchable: true,
                    toSearch: [],
                    cm: new Ext.grid.ColumnModel([
                        this.selModel,
                        {
                            header: "Chave",
                            dataIndex: "pk",
                            width: 45,
                            sortable: true
                        },

                        {
                            header: "Descrição",
                            dataIndex: "description",
                            sortable: true,
                            width: 550 - 105
                        }
                    ]),
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: 'Selecionar',
                            handler: this.send,
                            scope: this
                        },
                        {
                            text: 'Cancelar',
                            handler: function() {
                                this.destroy();
                            },
                            scope: this
                        }
                    ]
                });

                var cf = {
                    title: "Seletor de itens",
                    layout: "fit",
                    width: 550,
                    height: 325,
                    modal: true,
                    items: [
                        this.grid
                    ]
                };

                toolkit.plugins.ModelMultipleSelectForm.superclass.constructor.call(this, cf);
            }
        }
    );

    toolkit.plugins.MultiSelectField = Ext.extend(
        Ext.form.Field,
        {
            createEditForm: function(controller, fieldId, fieldText, record) {
                var scope = {
                    father : {
                        controller: controller,
                        id: "tbm",
                        reload_grid: function() {
                        }
                    },
                    form: false
                };

                scope.form = new toolkit.widget.ExtCrudForm(scope.father, 2, record.get("pk"));

                scope.form.fId = (typeof(fieldId) == 'object' ? fieldId : document.getElementById(fieldId));
                scope.form.fText = (typeof(fieldText) == 'object' ? fieldText : document.getElementById(fieldText));

                scope.form.action_commit_ex = scope.form.action_commit;
                scope.form.action_commit = function(type) {
                    var r = this.action_commit_ex(type);

                    this.fText.getAt(
                            this.fText.find(
                                    "pk",
                                    r.cid
                                    )
                            ).set("description", r.cvalue);

                    return r;
                }

                scope.form.show();
            },

            createAddForm: function(controller, fieldId, fieldText) {
                var scope = {
                    father : {
                        controller: controller,
                        id: "tbm",
                        reload_grid: function() {
                        }
                    },
                    form: false
                };

                scope.form = new toolkit.widget.ExtCrudForm(scope.father, 1);

                scope.form.fId = (typeof(fieldId) == 'object' ? fieldId : document.getElementById(fieldId));
                scope.form.fText = (typeof(fieldText) == 'object' ? fieldText : document.getElementById(fieldText));

                scope.form.action_commit_ex = scope.form.action_commit;
                scope.form.action_commit = function(type) {
                    var r = this.action_commit_ex(type);
                    var item = document.createElement("option");
                    item.selected = true;
                    item.value = r.cid;
                    this.fId.appendChild(item);

                    this.fText.add(new Ext.data.Record({pk: r.cid, description: r.cvalue}));

                    return r;
                }

                scope.form.show();

            },

            constructor: function(cf) {
                if (cf.conf == undefined)
                    cf.conf = {
                        canAdd: false,
                        canEdit: false
                    }
                else {
                    cf.conf.canAdd = cf.conf.canAdd == undefined ? true : cf.conf.canAdd;
                    cf.conf.canEdit = cf.conf.canEdit == undefined ? true : cf.conf.canEdit;
                }

                toolkit.plugins.MultiSelectField.superclass.constructor.call(this, cf);
            },

            setWidth: function(width) {
                if(width < 120) width = 120;

                this.grid.setWidth(width);
                this._getAutocompleteField().setWidth(width - 90);

                toolkit.plugins.MultiSelectField.superclass.setWidth.call(this, width);
            },

            _getAutocompleteField: function() {
                if(!this._autoCompleteField)
                    this._autoCompleteField = new toolkit.plugins.AutoCompleteField2({
                        'toolbarInside': true,
                        'submitValue': false,
                        'autoHeight': true,
                        'width': (this.width - 75),
                        'displayField': 'description',
                        'allowBlank': true,
                        'value': null,
                        'valueField': 'pk',
                        'conf': {
                            'addLabel': 'Criar ...',
                            'editLabel': 'Modificar ...',
                            'canAdd': this.conf.canAdd,
                            'canEdit': this.conf.canEdit
                        },
                        'triggerAction': 'all',
                        'queryAction': (this.queryAction ? this.queryAction : 'query'),
                        'hideTrigger': true,
                        'queryParam': 'keyword',
                        'crudController': this.controller,
                        'enableKeyEvents': true,
                        'listeners': {
                            'scope': this,
                            'select': function(field, record) {
                                var store = this.grid.getStore();
                                var item = document.createElement('option');

                                if(record) {
                                    store.add(record);
                                    field.clearValue();
                                    field.setValue('');
                                    field.focus();

                                    item.selected = true;
                                    item.value = record.get('pk');
                                    item.innerHTML = record.get('description');
                                    this.getEl().dom.appendChild(item);
                                }
                            },
                            'specialkey': function(field, e) {
                                if(e.getKey() == e.ENTER) {
                                    var pk = field.getValue();
                                    var store = field.getStore();
                                    var record = store.getAt(store.find('pk', pk));

                                    field.fireEvent('select', field, record);
                                }
                            }
                        }
                    });

                return this._autoCompleteField;
            },

            setValue: function(value) {
                var flag = true;

                if(this.store && value && (value.length > 0 && Ext.isArray(value[0]) || value.length == 0)) {
                    try {
                        this.store.removeAll();

                        while (flag) {
                            var el = this.getEl().first();
                            if(el) el.remove()
                            else flag = false
                        }
                    }
                    catch(e) {}


                    Ext.each(
                        value,
                        function(tupla) {
                            try {
                                this.store.add(new Ext.data.Record({
                                    'pk': tupla[0],
                                    'description': (tupla[1] ? tupla[1] : 'BUG'),
                                }));

                                var opt = this.getEl().createChild({
                                    'tag': 'option',
                                    'selected': true,
                                    'value': tupla[0],
                                    'html': (tupla[1] ? tupla[1] : 'BUG')
                                });
                            }
                            catch(e) {}
                        },
                        this
                    );
                }
                else toolkit.plugins.MultiSelectField.superclass.setValue.call(this, value);
            },

            onRender: function(container, position) {
                var data = [];
                var values = this.getValues();
                var descs = this.getDescriptions();

                for (var idx in values) {
                    if (typeof(descs[idx]) != "function")
                        data.push({
                            pk: values[idx],
                            desc: descs[idx]
                        });
                }

                var conf = {
                    name: this.name,
                    options: data
                };

                var tpl = new Ext.XTemplate(
                    '<select name="{name}" id="{name}" multiple size="10">',
                    '<tpl for=\"options\">',
                        '<option value="{pk}" selected>{desc}</option>',
                    '</tpl>',
                    '</select>'
                );

                if (this.value == undefined)
                    this.value = []

                this.store = new Ext.data.SimpleStore({
                    fields: ["pk", "description"],
                    data: this.value
                });

                if (values.length > 0)
                    this.value = values;
                else
                    this.value = null;

                this.width = this.width ? this.width : container.getBox().width;
                this.grid = new Ext.grid.GridPanel({
                    cm: new Ext.grid.ColumnModel([
                        {
                            header: "Chave",
                            dataIndex: "pk",
                            width: 45,
                            sortable: true
                        },
                        {
                            header: "Descrição",
                            dataIndex: "description",
                            sortable: true,
                            width: this.width - 65
                        },
                    ]),
                    title: this.title !== undefined ? this.title : undefined,
                    border: this.border !== undefined ? this.border : false,
                    frame: this.frame !== undefined ? this.frame : false,
                    store: this.store,
                    height: this.height !== undefined ? this.height : 175,
                    width: this.width + 1,
                    renderTo: container,
                    tbar: [
                        ' ',
                        {
                            text: 'Buscar :',
                            xtype: 'label'
                        },
                        ' ',
                        this._getAutocompleteField()
                    ],
                    bbar: [
                        {
                            text: 'Selecionar',
                            tooltip: 'Abre umas caixa com multipla seleção.',
                            scope: this,
                            handler: this.addForm,
                            icon: "/" + global.Context + '/static/images/format-list-unordered.png'
                        },
                        {
                            text: 'Limpar',
                            tooltip: 'Limpa toda a caixa de seleção.',
                            icon: "/" + global.Context + "/static/images/clear-all.png",
                            scope: this,
                            handler: this.doClear
                        },
                        {
                            text: 'Retirar',
                            tooltip: 'Retira somente os itens que estão selecionados.',
                            icon: "/" + global.Context + "/static/images/clear-selected.png",
                            scope: this,
                            handler: this.unSelectItem
                        },
                        '-',
                        '->',
                        '-'
                    ]
                });

                if (this.controller && (this.conf.canAdd || this.conf.canEdit)) {
                    this.grid.getBottomToolbar().addButton(this.getButtons(this));
                    this.grid.getBottomToolbar().add("-");
                }

                this.el = tpl.append(container, conf, true);
                this.el.dom.style.display = "none";

                /**
                 * FIXME:
                 * Bug no chrome força a inclusão do remédio logo abaixo.
                 * Options mesmo com selected explicito não estava selecionando os elementos.
                 */
                Ext.each(
                    this.el.query('option'),
                    function(node) {
                        setTimeout(
                            function() {
                                node.selected = true;
                            },
                            500
                        );
                    }
                );
            },

            _doRemoveOnSelect: function(pkValue) {
                var select = this.getEl().dom;
                var flag = false;

                Ext.each(select.childNodes, function(option) {
                    if(option.value == pkValue) {
                        select.removeChild(option);
                        flag = true;
                    }

                    return !flag;
                });

                return flag
            },

            doClear: function() {
                var store = this.grid.getStore();
                store.each(
                    function(record) {
                        if(this._doRemoveOnSelect(record.get('pk')))
                            store.remove(record);
                    },
                    this
                );
            },

            unSelectItem: function() {
                var selection = this.grid.getSelectionModel().getSelections();
                var store = this.grid.getStore();

                if(selection.length > 0) {
                    Ext.each(
                        selection,
                        function(record) {
                            if(this._doRemoveOnSelect(record.get('pk')))
                                store.remove(record);
                        },
                        this
                    );
                }
                else Ext.Msg.show({
                    'title': 'Remover selecionados',
                    'msg': 'Primeiro seleciona um item para poder remover dos itens selecionados',
                    'icon': Ext.Msg.ERROR,
                    'buttons': Ext.Msg.OK
                });
            },

            getButtons: function(father){
                var buttons = [];
                if(father.conf.canAdd)
                    buttons.push({
                        iconCls: true,
                        text: "Novo",
                        icon: "/" + global.Context + "/static/images/appointment-new.png",
                        handler: function() {
                            father.createAddForm(father.controller, father.name, father.store);
                        },
                        scope: this
                    });
                if(father.conf.canEdit)
                    buttons.push({
                        iconCls: true,
                        text: "Editar",
                        icon: "/" + global.Context + "/static/images/edit.png",
                        handler: function() {
                            var selection = father.grid.getSelectionModel();
                            var obj = father;

                            selection.each(
                                function(record) {
                                    obj.createEditForm(obj.controller, obj.name, obj.store, record)
                                }
                            );
                        },
                        scope: this
                    });
                return buttons;
            },

            addForm: function() {
                new toolkit.plugins.ModelMultipleSelectForm(
                    (this.model ? this.model.name : null),
                    (this.model ? this.model.pkg : null),
                    this
                ).show();
            },

            remove: function() {
                var sels = this.grid.getSelectionModel().getSelections();
                var pks = [];
                var opts = [];

                for (var idx in sels) {
                    var sel = sels[idx];

                    if (typeof(sel) != "function")
                        pks.push(sel.data["pk"]);
                }

                for (var idx in this.el.dom.childNodes) {
                    var opt = this.el.dom.childNodes[idx];

                    if (opt != undefined && opt.value != undefined) {
                        for (var i in pks) {
                            if (opt.value == pks[i])
                                opt.selected = false;
                        }
                    }
                }

                for (var i in sels) {
                    this.store.remove(sels[i]);
                }
            },

            getValues: function() {
                var result = [];
                var row;

                for (var idx in this.value) {
                    row = this.value[idx]
                    if (row[0]) result.push(row[0]);
                }

                return result;
            },

            getDescriptions: function() {
                var result = [];
                var row;

                for (var idx in this.value) {
                    row = this.value[idx]
                    if (row[1]) result.push(row[1]);
                }

                return result;
            }
        }
    );

    toolkit.plugins.MultiSelectFieldCustom = Ext.extend(
        toolkit.plugins.MultiSelectField,
        {
             addForm: function() {
                new toolkit.plugins.ModelMultipleSelectFormCustom(
                        this.model.name,
                        this.model.pkg,
                        this,
                        'query_rh'
                    ).show();
            }
        }
    );

    Ext.reg("multiselectbox", toolkit.plugins.MultiSelectField);

    Ext.reg("multiselectboxcustom", toolkit.plugins.MultiSelectFieldCustom);

    toolkit.plugins.CPFInputField = Ext.extend(
        Ext.form.TextField,
        {
            constructor: function(cf) {
                cf.validateOnBlur = true;
                cf.validationEvent = false;
                toolkit.plugins.CPFInputField.superclass.constructor.call(this, cf);
            },

            validate: function() {
                var result = false;

                var value = this.clean(this.el.dom.value);

                if (value == "" && this.allowBlank)
                    return true;

                var notValids = [
                    '00000000000',
                    '11111111111',
                    '22222222222',
                    '33333333333',
                    '44444444444',
                    '55555555555',
                    '66666666666',
                    '77777777777',
                    '88888888888',
                    '99999999999',
                    '12345678909'
                ];

                var flag = false;
                for (var idx in notValids) {
                    var r = notValids[idx];

                    if (typeof(r) != "function")
                        flag = (r == value)

                    if (flag) {
                        this.markInvalid("Este CPF está na lista negra.");
                        return false;
                    }
                }

                if (!flag) {
                    var sm = 0;
                    var mod = 11;
                    var rst = 0;
                    var dgt = "";
                    var i;

                    for (i = 0; i < 9; i++) {
                        sm += (value[i] * (--mod));
                    }

                    if ((rst = sm % 11) < 2)
                        dgt += "0"
                    else
                        dgt += "" + (11 - rst);

                    sm = 0;
                    mod = 11;

                    for (i = 0; i < 10; i++) {
                        sm += (value[i] * (mod--));
                    }

                    if ((rst = sm % 11) < 2)
                        dgt += "0"
                    else
                        dgt += "" + (11 - rst);

                    result = (value.substring(9) == dgt);
                }

                if (!result) this.markInvalid("Dígito verificador inválido.");
                else this.clearInvalid();

                return result;
            },

            clean: function(value) {
                var clean = value;
                var exp = /[\.|-]/;

                while (clean.indexOf('.') > 0 || clean.indexOf('-') > 0)
                    clean = clean.replace(exp, "");

                return clean;
            },

            format: function(value) {
                var result = "";

                for (var i = 0; i < value.length; i++) {
                    if (i == 3 || i == 6) result += ".";
                    else if (i == 9) result += "-";

                    result += value[i];
                }

                return result;
            },

            onRender: function(container, position) {
                toolkit.plugins.CPFInputField.superclass.onRender.call(this, container, position);

                var tpl = new Ext.XTemplate('<input type="hidden" name="{name}" value="{value}">');
                this.input = tpl.append(
                    container,
                    {
                        name: this.name,
                        value: this.value
                    },
                    true
                );

                var inp = this.el.dom;
                var obj = this.input.dom;
                var self = this;

                inp.maxLength = 14;

                this.el.dom.onblur = function() {
                    obj.value = self.clean(inp.value);
                    self.validate();
                }

                this.el.dom.onkeypress = function(event) {
                    var result;

                    if (event.keyCode != 0) {
                        result = true;
                    }
                    else {
                        if (event.charCode >= 48 && event.charCode <= 57)
                            result = true;
                        else
                            result = false;
                    }

                    if (result && event.keyCode == 0) {
                        if (inp.value.length == 3 || inp.value.length == 7)
                            inp.value += ".";
                        else if (inp.value.length == 11)
                            inp.value += "-";
                    }

                    return result;
                }

                this.el.dom.name = "";
                if (this.value != undefined) this.value = this.format(this.value);
            }
        }
    );

    Ext.reg("cpffield", toolkit.plugins.CPFInputField);

    toolkit.plugins.FoneInputField = Ext.extend(
        Ext.form.Field,
        {
            clean: function(value) {
                var clean = value;

                clean = clean.replace("(", "");
                clean = clean.replace(")", "");
                clean = clean.replace(" ", "");
                clean = clean.replace("-", "");

                return clean;
            },

            validate: function() {
                return true;
            },

            format: function(value) {
                var result = "";

                for (var i = 0; i < value.length; i++) {
                    if (i == 0) result += "(";
                    else if (i == 2) result += ") ";
                    else if (i == 6) result += "-";

                    result += value[i];
                }

                return result;
            },

            onRender: function(container, position) {
                toolkit.plugins.FoneInputField.superclass.onRender.call(
                    this,
                    container,
                    position
                );

                if (this.value) {
                    var swap = this.value;

                    while (swap.indexOf("-") != -1)
                        swap = swap.replace(/-/, '');

                    this.value = swap;
                }

                var tpl = new Ext.XTemplate('<input type="hidden" name="{name}" value="{value}">');
                this.input = tpl.append(
                    container,
                    {
                        name: this.name,
                        value: this.value
                    },
                    true
                );

                this.el.dom.name = "";
                this.el.dom.maxLength = 14;

                var inp = this.el.dom;
                var obj = this.input.dom;
                var self = this;

                this.el.dom.onkeypress = function(event) {
                    var result;

                    if (event.keyCode != 0) {
                        result = true;
                    }
                    else {
                        if (event.charCode >= 48 && event.charCode <= 57)
                            result = true;
                        else
                            result = false;
                    }

                    if (result && event.keyCode == 0) {
                        if (inp.value.length == 0)
                            inp.value = "(";
                        else if (inp.value.length == 3)
                            inp.value += ") ";
                        else if (inp.value.length == 9)
                            inp.value += "-";
                        else if (inp.value.length == 1)
                            inp.value = "("+inp.value;
                    }

                    return result;
                };

                this.el.dom.onblur = function() {
                    obj.value = self.clean(inp.value);
                    self.validate();
                }

            },

            setValue : function(v){
                this.value = this.clean(v);
                if(this.rendered){
                    this.input.dom.value = (Ext.isEmpty(v) ? '' : this.clean(v));
                    this.el.dom.value = (Ext.isEmpty(v) ? '' : this.format(v));
                    this.validate();
                }
                return this;
            }
        }
    );

    // Ext.reg("fonefield", toolkit.plugins.FoneInputField);

    toolkit.plugins.CEPInputField = Ext.extend(
        Ext.form.Field,
        {
            clean: function(value) {
                var clean = value;
                return clean;
            },

            validate: function() {
                return true;
            },

            format: function(value) {
                var result = "";

                while (value.indexOf("-") > 0)
                    value = value.replace("-", "");

                for (var i = 0; i < value.length; i++) {
                    if (i == 5) result += "-";
                    result += value[i];
                }

                return result;
            },

            onRender: function(container, position) {
                toolkit.plugins.CEPInputField.superclass.onRender.call(
                    this,
                    container,
                    position
                );

                var tpl = new Ext.XTemplate('<input type="hidden" name="{name}" value="{value}">');
                this.input = tpl.append(
                    container,
                    {
                        name: this.name,
                        value: this.value
                    },
                    true
                );

                this.el.dom.name = "";
                this.el.dom.maxLength = 9;

                var inp = this.el.dom;
                var obj = this.input.dom;
                var self = this;

                this.el.dom.onkeypress = function(event) {
                    var result;

                    if (event.keyCode != 0) {
                        result = true;
                    }
                    else {
                        if (event.charCode >= 48 && event.charCode <= 57)
                            result = true;
                        else
                            result = false;
                    }

                    if (result && event.keyCode == 0) {
                        if (inp.value.length == 5)
                            inp.value += "-";
                    }

                    return result;
                };

                this.el.dom.onblur = function() {
                    obj.value = self.clean(inp.value);
                    self.validate();
                }

                if (this.value != undefined) this.value = this.format(this.value);
            }
        }
    );

    Ext.reg("cepfield", toolkit.plugins.CEPInputField);

    toolkit.plugins.CNPJInputField = Ext.extend(
        Ext.form.Field,
        {
            clean: function(value) {
                var cl = value;

                cl = cl.replace(".", "");
                cl = cl.replace(".", "");
                cl = cl.replace("/", "");
                cl = cl.replace("-", "");

                return cl;
            },

            validate: function() {
                var seq = [
                    [5,4,3,2,9,8,7,6,5,4,3,2],
                    [6,5,4,3,2,9,8,7,6,5,4,3,2]
                ];

                var sm = 0;
                var idx, rst;
                var value = this.clean(this.el.dom.value);

                if (value == "" && this.allowBlank)
                    return true;

                var dgt = "";

                if (value.length == 14) {
                    for (idx = 0; idx < seq[0].length; idx++) {
                        sm += (value[idx] * seq[0][idx]);
                    }

                    if ((rst = sm % 11) < 2)
                        dgt += "0"
                    else
                        dgt += "" + (11 - rst);

                    sm = 0;
                    for (idx = 0; idx < seq[1].length; idx++) {
                        sm += (value[idx] * seq[1][idx]);
                    }

                    if ((rst = sm % 11) < 2)
                        dgt += "0"
                    else
                        dgt += "" + (11 - rst);

                    if (dgt != value.substring(12)) {
                        this.markInvalid("Este CNPJ não é válido.");
                    }
                    else {
                        this.clearInvalid();
                    }

                }
                else {
                    this.markInvalid("O CNPJ deve ter 14 dígitos.");
                }

                return true;
            },

            format: function(value) {
                var result = "";

                for (var i = 0; i < value.length; i++) {
                    if (i == 2 || i == 5) result += ".";
                    else if (i == 8) result += "/";
                    else if (i == 12) result += "-";

                    result += value[i];
                }

                return result;
            },

            onRender: function(container, position) {
                toolkit.plugins.CEPInputField.superclass.onRender.call(
                        this,
                        container,
                        position
                        );

                var tpl = new Ext.XTemplate('<input type="hidden" name="{name}" value="{value}">');
                this.input = tpl.append(
                        container,
                {
                    name: this.name,
                    value: this.value
                },
                        true
                        );

                this.el.dom.name = "";
                this.el.dom.maxLength = 18;

                var inp = this.el.dom;
                var obj = this.input.dom;
                var self = this;

                this.el.dom.onkeypress = function(event) {
                    var result;

                    if (event.keyCode != 0) {
                        result = true;
                    }
                    else {
                        if (event.charCode >= 48 && event.charCode <= 57)
                            result = true;
                        else
                            result = false;
                    }

                    if (result && event.keyCode == 0) {
                        if (inp.value.length == 2 || inp.value.length == 6)
                            inp.value += ".";
                        else if (inp.value.length == 10)
                            inp.value += "/";
                        else if (inp.value.length == 15)
                            inp.value += "-";

                    }

                    return result;
                };

                this.el.dom.onblur = function() {
                    obj.value = self.clean(inp.value);
                    self.validate();
                }

                if (this.value != undefined) this.value = this.format(this.value);
            }
        }
    );

    Ext.reg("cnpjfield", toolkit.plugins.CNPJInputField);

    toolkit.plugins.WindowSelectFile = Ext.extend(
        Ext.Window,
        {
            rendererByte: function(text) {
                var types = [
                    "B",
                    "KB",
                    "MB",
                    "GB",
                    "TB"
                ];

                var number = eval(text);
                var type = 0;
                for (type in types) {
                    if (number < 1000)
                        break
                    else {
                        number = number / 1024;
                    }
                }

                return "<p style=\"text-align:right\">" + number.toFixed(2) + " " + types[type] + "</p>";
            },

            _selectFile: function() {
                var node = this.grid.getSelectionModel().getSelected();
                this.father.setValue(node.get("pk"));
                this.destroy();
            },

            createGridStore: function() {
                return new Ext.data.JsonStore({
                    root: "result",
                    url: toolkit.util.Normalize.controller_action(
                            this._controller,
                            "list_files"
                            ),
                    fields: [
                        "pk",
                        "filename",
                        "size",
                        "owner"
                    ]
                });
            },

            constructor: function(father) {

                this.father = father;
                this.controller = father.controller || 'FileUploadController';
                this.storeGrid = this.createGridStore();

                this.grid = new Ext.grid.GridPanel({
                    region: "center",
                    border: true,
                    xtype: "grid",
                    cm: new Ext.grid.ColumnModel([
                        {dataIndex: "filename", header: "Arquivo", width: 255, sortable: true},
                        {dataIndex: "size", header: "Tamanho", width: 85, renderer: this.rendererByte},
                        {dataIndex: "owner", header: "Criado", width: 75},
                    ]),
                    sm: new Ext.grid.RowSelectionModel({
                        singleSelect: true
                    }),
                    store: this.storeGrid
                });

                var cf = {
                    title: "Selecionar arquivo",
                    closable: true,
                    width: 630,
                    height: 300,
                    layout: "border",
                    border: false,
                    frame: true,
                    items: [
                        {
                            region: "west",
                            width: 175,
                            split: true,
                            minWidth: 175,
                            border: true,
                            xtype: "treepanel",
                            line: false,
                            root: {
                                text: "Raiz",
                                id: '0'
                            },
                            listeners: {
                                scope: this,
                                click: function(node) {
                                    if (node.isLeaf()) {
                                        this.storeGrid.load({
                                            params: {
                                                level: node.id
                                            }
                                        });
                                    }
                                }
                            },
                            loader: new Ext.tree.TreeLoader({
                                url: toolkit.util.Normalize.controller_action(
                                        this.controller,
                                        "list_dir"
                                        )
                            })
                        },
                        this.grid
                    ],
                    buttons: [
                        {
                            text: "Selecionar",
                            scope: this,
                            handler: this._selectFile
                        },
                        {
                            text: "Cancelar",
                            scope: this,
                            handler: function() {
                                this.destroy();
                            }
                        }
                    ]
                };

                toolkit.plugins.WindowSelectFile.superclass.constructor.call(this, cf)
            }
        }
    );

    toolkit.plugins.WindowSendFile = Ext.extend(
        Ext.Window,
        {
            createForm: function() {
                var form = new Ext.form.FormPanel({
                    style: "margin: 5pt",
                    border: false,
                    labelWidth: 60,
                    fileUpload: true,
                    defaults: {
                        width: 250
                    },
                    items: [
                        {
                            name: "file",
                            xtype: "fileuploadfield",
                            fieldLabel: "Arquivo",
                            buttonCfg: {
                                iconCls: true,
                                icon: "/" + global.Context + "/static/images/upload.png",
                                text: ""
                            },
                            listeners: {
                                scope: this,
                                render: function(cmp)
                                {
                                    var field = this.form.findByType('fileuploadfield')[0];
                                    field.fileInput.dom.click();
                                }
                            },
                        },
                        {
                            xtype: 'textfield',
                            inputType: 'hidden',
                            name: 'acesso',
                            value: '3'
                        }
                        // {
                        //     hiddenName: "acesso",
                        //     xtype: "combo",
                        //     fieldLabel: "Acesso",
                        //     value: 3,
                        //     editable: false,
                        //     triggerAction: 'all',
                        //     store: [
                        //         [1, "PRIVADO"],
                        //         [2, "PRIVADO PARA O GRUPO"],
                        //         [3, "PÚBLICO"],
                        //     ]
                        // }
                    ]
                });

                return form;
            },

            uploadFile: function() {
                var form = this.form.getForm();
                var url = toolkit.util.Normalize.controller_action(
                        this.controller,
                        "load"
                        );

                try {
                    form.submit({
                        scope: this,
                        clientValidation: true,
                        url: url,
                        waitMsg: "Enviando arquivo para o servidor...",
                        success: function(frm, action) {
                            this.father.setValue(action.result.file_id);
                            this.father.observeFileUploaded(action.result);
                            this.destroy();
                        },
                        failure: function(frm, action) {
                            var msg = Ext.util.Format.stripTags(action.response.responseText);

                            if (Ext.isString(action.result.msg)) {
                                msg = action.result.msg
                            } else if (action.response.responseText.indexOf('413') > -1) {
                                msg = 'O tamanho do arquivo excedeu o limite máximo.';
                            }

                            Ext.Msg.show({
                                title: 'Enviando arquivo',
                                msg: msg,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    });
                }
                catch(e) {
                    console.debug(e);
                }
            },

            _clear: function() {
                this.form.getForm().reset();
            },

            constructor: function(father) {
                father = father || {};
                father.observeFileUploaded = father.observeFileUploaded || function(result){console.debug('not implemented');};
                this.father = father;
                this.controller = father.controller || 'FileUploadController';

                this.form = this.createForm();

                var cf = {
                    title: "Anexar arquivo",
                    closable: true,
                    modal: true,
                    items: new Ext.Panel({
                        border: false,
                        items: this.form
                    }),
                    width: 350,
                    buttons: [
                        {
                            text: "Anexar",
                            handler: this.uploadFile,
                            scope: this
                        },
                        {
                            text: "Cancelar",
                            scope: this,
                            handler: function() {
                                this.destroy();
                            }
                        }
                    ]
                }

                toolkit.plugins.WindowSendFile.superclass.constructor.call(this, cf);
            }
        }
    );

    toolkit.plugins.SimpleFileUpload = Ext.extend(Ext.form.CompositeField, {
        constructor: function(params)
        {
            var config = Ext.apply({
                items: this.getItems(params),
                listeners:
                {
                    scope: this,
                    render: function(cmp)
                    {
                        if(this.getValue())
                            this.getFileInfo();
                    }

                }
            }, params);

            config = Ext.applyIf(config, {showMessageFileInfoErr: true});

            toolkit.plugins.SimpleFileUpload.superclass.constructor.call(this, config);

            this._hiddenField = this.items.get(0);
            this._displayField = this.items.get(1);

            this.name = this.name + "-filefield-container";
        },

        getItems: function(params){
            var items = [
                {
                    xtype: 'hidden',
                    name: params.name
                },
                {
                    xtype: 'textfield',
                    fieldLabel: "Arquivo",
                    disabled: true,
                    width: '65%'
                },
            ];
            return items.concat(this.getButtons(params));
        },

        getButtons: function(params){
            return [{
                    xtype: 'button',
                    tooltip: 'Selecionar arquivo',
                    icon: "/" + global.Context + "/static/images/upload.png",
                    handler: this._uploadWindow,
                    scope: this
                },
                {
                    xtype: 'button',
                    tooltip: 'Fazer download',
                    // hidden: true,
                    icon: "/" + global.Context + "/static/images/download.png",
                    handler: function()
                    {
                        if(this._url)
                            open(this._url, '_blank');
                        else
                            Ext.Msg.alert('Aviso', 'Primeiro é necessário fazer upload do arquivo.');
                    },
                    scope: this
                },
            ];
        },

        getFileInfo: function()
        {
            Ext.Ajax.request({
                scope: this,
                url: toolkit.util.action('FileUploadController/get_file_info'),
                method: 'POST',
                params: { pk: this._hiddenField.getValue() },
                success: function(response)
                {
                    var obj = Ext.decode(response.responseText);
                    if(obj.success)
                    {
                        this._url = obj.file_url;
                        this.innerCt.items.get(3).show();  // Exibindo botão de download
                        this.setDisplayValue(obj.file_path);
                    }
                    else if(this.showMessageFileInfoErr == true){
                        Ext.Msg.alert('Erro', obj.message);
                    }
                },
                failure: function(response)
                {
                    if(this.showMessageFileInfoErr == true){
                        Ext.Msg.alert('Erro', 'Não foi possível recuperar informações do arquivo.');
                    }
                }
            });
        },

        setValues: function(result)
        {
            this.setValue(result.file_id)
            this.setDisplayValue(result.file_store);
        },

        setValue: function(val)
        {
            this._hiddenField.setValue(val);
            this.getFileInfo();
        },

        getValue: function()
        { return this._hiddenField.getValue(); },

        setDisplayValue: function(val)
        {
            var oldVal = this.getDisplayValue();
            this._displayField.setValue(val);

            /* Callback criado devido ao evento change não se comportar como esperado com composite field */
            this.fireEvent('afterchange', this, val, oldVal);
        },

        getDisplayValue: function()
        { return this._displayField.getValue(); },

        // observeFileUploaded: function(result)
        // { this.setDisplayValue(result.file_store); },

        _uploadWindow: function()
        {
            var uploadWindow = new toolkit.plugins.WindowSendFile(this);
            uploadWindow.show();
        }
    });

    Ext.reg('ged-fileuploadfield', toolkit.plugins.SimpleFileUpload);

    toolkit.plugins.FileUpload = Ext.extend(
        Ext.form.TextField,
        {
            ALGORITHM: {
                MD5: "md5",
                SHA128: "sha128",
                CRC32: "crc32"
            },

            constructor: function(cf) {
                cf.width = cf.width - 45;
                cf.disabled = true;
                cf.controller = cf.controller || 'FileUploadController';

                if (cf.value instanceof Array) {
                    cf.value = cf.value[1];
                }

                toolkit.plugins.FileUpload.superclass.constructor.call(this, cf);
            },

            _selectFile: function() {
                var frm = new toolkit.plugins.WindowSelectFile(this);
                frm.show();
            },

            _downloadFile: function() {
                if (this.getValue() != "") {
                    var url = toolkit.util.Normalize.controller_action(
                            this.controller,
                            "get_file",
                            [this.getValue()]
                            );

                    var width = 235;
                    var height = 175;
                    var left = (screen.width - width) / 2;
                    var top = (screen.height - height) / 2;
                    window.open(url, "buildFile", "status=no, width=" + width + ", height=" + height + ", toolbar=no, resizable=no, left=" + left + ", top=" + top);
                }
                else {
                    alert("Primeiro deve ser selecionado um arquivo.");
                }
            },

            _signFile: function() {
                if (this.getValue() != "") {
                    var url = toolkit.util.Normalize.controller_action(
                            this.controller,
                            "sign",
                            [this.getValue()]
                            );

                    var width = 235;
                    var height = 175;
                    var left = (screen.width - width) / 2;
                    var top = (screen.height - height) / 2;
                    window.open(url, "buildFile", "status=no, width=" + width + ", height=" + height + ", toolbar=no, resizable=no, left=" + left + ", top=" + top);
                }
                else {
                    alert("Primeiro deve ser selecionado um arquivo.");
                }
            },

            _validateFile: function() {
                console.debug(alg);
            },

            _uploadFile: function() {
                var frm = new toolkit.plugins.WindowSendFile(this);
                frm.show();
            },

            _clear: function() {
                this.setValue("");
            },

            setValue: function(new_value) {
                if(this.hiddenInput) {
                    this.hiddenInput.setValue(new_value);
                    if (new_value != undefined && new_value != "") {
                        var obj = toolkit.util.Ajax.request_json(
                            "POST",
                            toolkit.util.Normalize.controller_action(
                                this.controller,
                                "get_value"
                            ),
                            {
                                pk: this.hiddenInput.getValue()
                            }
                        );

                        toolkit.plugins.FileUpload.superclass.setValue.call(this, obj.value);
                    }
                    else toolkit.plugins.FileUpload.superclass.setValue.call(this, "");
                }
                else this.value = new_value;
            },

            getValue: function() {
                return this.hiddenInput.getValue();
            },

            onRender: function(container, position) {
                var input = new Ext.Panel({
                    border: false
                });
                this.hiddenInput = new Ext.form.TextField({
                    inputType: 'hidden',
                    name: this.name
                });

                new Ext.Panel({
                    renderTo: container,
                    border: false,
                    layout: "table",
                    items: [
                        input,
                        this.hiddenInput,
                        {
                            xtype: "panel",
                            border: false,
                            items: [
                                {
                                    xtype: "button",
                                    style: "margin: 0 0 0 5pt",
                                    iconCls: true,
                                    icon: "/" + global.Context + "/static/images/view-sort-ascending.png",
                                    menu: [
                                        {
                                            text: "Limpar",
                                            scope: this,
                                            iconCls: true,
                                            handler: this._clear,
                                            icon: "/" + global.Context + "/static/images/edit-clear-locationbar-rtl.png"
                                        },
                                        "-",
                                        {
                                            text: "Anexar",
                                            handler: this._uploadFile,
                                            scope: this,
                                            iconCls: true,
                                            icon: "/" + global.Context + "/static/images/upload.png"
                                        },
                                        {
                                            text: "Selecionar",
                                            handler: this._selectFile,
                                            scope: this,
                                            iconCls: true,
                                            icon: "/" + global.Context + "/static/images/document-export.png"
                                        },
                                        "-",
                                        {
                                            text: "Fazer download",
                                            handler: this._downloadFile,
                                            scope: this,iconCls: true,
                                            icon: "/" + global.Context + "/static/images/download.png"
                                        },
                                        //                                        "-",
                                        //                                        {
                                        //                                            text: "Assinatura",
                                        //                                            handler: this._signFile,
                                        //                                            scope: this,iconCls: true,
                                        //                                            icon: "/" + global.Context + "/static/images/document-sing.png"
                                        //                                        },
                                        //                                        {
                                        //                                            text: "Checar assinatura",
                                        //                                            handler: this._validateFile,
                                        //                                            scope: this,iconCls: true,
                                        //                                            icon: "/" + global.Context + "/static/images/edit.png"
                                        //                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                });

                toolkit.plugins.FileUpload.superclass.onRender.call(this, input.body);
                this.el.dom.name = "";
            }
        }
    );

    Ext.reg('ged-fileuploadfield-2', toolkit.plugins.FileUpload);

    toolkit.plugins.SimpleFileUpload = Ext.extend(Ext.form.CompositeField, {
        constructor: function(params)
        {
            var config = Ext.apply({
                items: this.getItems(params),
                listeners:
                {
                    scope: this,
                    render: function(cmp)
                    {
                        if(this.getValue())
                            this.getFileInfo();
                    }

                }
            }, params);

            config = Ext.applyIf(config, {showMessageFileInfoErr: true});

            toolkit.plugins.SimpleFileUpload.superclass.constructor.call(this, config);

            this._hiddenField = this.items.get(0);
            this._displayField = this.items.get(1);

            this.name = this.name + "-filefield-container";
        },

        getItems: function(params){
            var items = [
                {
                    xtype: 'hidden',
                    name: params.name
                },
                {
                    xtype: 'textfield',
                    fieldLabel: "Arquivo",
                    disabled: true,
                    width: '65%'
                },
            ];
            return items.concat(this.getButtons(params));
        },

        getButtons: function(params){
            return [{
                    xtype: 'button',
                    tooltip: 'Selecionar arquivo',
                    icon: "/" + global.Context + "/static/images/upload.png",
                    handler: this._uploadWindow,
                    scope: this
                },
                // {
                //     xtype: 'button',
                //     tooltip: 'Fazer download',
                //     // hidden: true,
                //     icon: "/" + global.Context + "/static/images/download.png",
                //     handler: function()
                //     {
                //         if(this._url)
                //             open(this._url, '_parent');
                //         else
                //             Ext.Msg.alert('Aviso', 'Primeiro é necessário fazer upload do arquivo.');
                //     },
                //     scope: this
                // },
            ];
        },

        getFileInfo: function()
        {
            Ext.Ajax.request({
                scope: this,
                url: toolkit.util.action('FileUploadController/get_file_info'),
                method: 'POST',
                params: { pk: this._hiddenField.getValue() },
                success: function(response)
                {
                    var obj = Ext.decode(response.responseText);
                    if(obj.success)
                    {
                        this._url = obj.file_url;
                        this.innerCt.items.get(3).show();  // Exibindo botão de download
                        this.setDisplayValue(obj.file_path);
                    }
                    else if(this.showMessageFileInfoErr == true){
                        Ext.Msg.alert('Erro', obj.message);
                    }
                },
                failure: function(response)
                {
                    if(this.showMessageFileInfoErr == true){
                        Ext.Msg.alert('Erro', 'Não foi possível recuperar informações do arquivo.');
                    }
                }
            });
        },

        setValues: function(result)
        {
            this.setValue(result.file_id)
            this.setDisplayValue(result.file_store);
        },

        setValue: function(val)
        {
            this._hiddenField.setValue(val);
            this.getFileInfo();
        },

        getValue: function()
        { return this._hiddenField.getValue(); },

        setDisplayValue: function(val)
        {
            var oldVal = this.getDisplayValue();
            this._displayField.setValue(val);

            /* Callback criado devido ao evento change não se comportar como esperado com composite field */
            this.fireEvent('afterchange', this, val, oldVal);
        },

        getDisplayValue: function()
        { return this._displayField.getValue(); },

        // observeFileUploaded: function(result)
        // { this.setDisplayValue(result.file_store); },

        _uploadWindow: function()
        {
            var uploadWindow = new toolkit.plugins.WindowSendFile(this);
            uploadWindow.show();
        }
    });

    Ext.reg('ged-fileuploadfield-3', toolkit.plugins.SimpleFileUpload);

    toolkit.plugins.WindowSendTypedFile = Ext.extend(
        toolkit.plugins.WindowSendFile,
        {
            createForm: function() {
                var form = toolkit.plugins.WindowSendTypedFile.superclass.createForm.call(this);

                form.add({
                    name: "types",
                    xtype: "textfield",
                    hidden: true,
                    labelSeparator: '',
                    value: Ext.util.JSON.encode(this.father.types)
                });

                return form;
            }
        }
    );

    toolkit.plugins.WindowSelectTypedFile = Ext.extend(
        toolkit.plugins.WindowSelectFile,
        {
            createGridStore: function() {
                var store = toolkit.plugins.WindowSelectTypedFile.superclass.createGridStore(this);
                store.baseParams["types"] = this.father.types;
                return store;
            }
        }
    );

    toolkit.plugins.TypedFileUpload = Ext.extend(
        toolkit.plugins.FileUpload,
        {
            _uploadFile: function() {
                var frm = new toolkit.plugins.WindowSendTypedFile(this);
                frm.show();
            },

            _selectFile: function() {
                var frm = new toolkit.plugins.WindowSelectTypedFile(this);
                frm.show();
            }
        }
    );
    Ext.reg('ged-typedfileuploadfield', toolkit.plugins.TypedFileUpload);

    toolkit.plugins.ImageUpload = Ext.extend(
        toolkit.plugins.SimpleFileUpload,
        {
            // observeFileUploaded: function(result){
            //     console.debug('not implemented');
            // }
            getButtons: function(params){
                var buttons = toolkit.plugins.ImageUpload.superclass.getButtons.call(this).concat({
                    xtype: 'button',
                    tooltip: 'Limpar',
                    icon: "/" + global.Context + "/static/images/edit-clear-locationbar-rtl.png",
                    handler: this._clear,
                    scope: this
                });
                return buttons;
            },

            _clear: function() {
                this.setDisplayValue('');
                this._hiddenField.setValue('');
                this.observeFileUploaded({file_id: undefined});
            },
        }
    );
    Ext.reg('ged-imageuploadfield', toolkit.plugins.ImageUpload);

    Ext.form.FileUploadField = Ext.extend(Ext.form.TextField, {
        /**
         * @cfg {String} buttonText The button text to display on the upload button (defaults to
         * 'Browse...').  Note that if you supply a value for {@link #buttonCfg}, the buttonCfg.text
         * value will be used instead if available.
         */
        buttonText: 'Browse...',
        /**
         * @cfg {Boolean} buttonOnly True to display the file upload field as a button with no visible
         * text field (defaults to false).  If true, all inherited TextField members will still be available.
         */
        buttonOnly: false,
        /**
         * @cfg {Number} buttonOffset The number of pixels of space reserved between the button and the text field
         * (defaults to 3).  Note that this only applies if {@link #buttonOnly} = false.
         */
        buttonOffset: 3,
        /**
         * @cfg {Object} buttonCfg A standard {@link Ext.Button} config object.
         */

        // private
        readOnly: true,

        /**
         * @hide
         * @method autoSize
         */
        autoSize: Ext.emptyFn,

        // private
        initComponent: function() {
            Ext.form.FileUploadField.superclass.initComponent.call(this);

            this.addEvents(
                /**
                 * @event fileselected
                 * Fires when the underlying file input field's value has changed from the user
                 * selecting a new file from the system file selection dialog.
                 * @param {Ext.form.FileUploadField} this
                 * @param {String} value The file value returned by the underlying file input field
                 */
                    'fileselected'
                    );
        },

        // private
        onRender : function(ct, position) {
            Ext.form.FileUploadField.superclass.onRender.call(this, ct, position);

            this.wrap = this.el.wrap({cls:'x-form-field-wrap x-form-file-wrap'});
            this.el.addClass('x-form-file-text');
            this.el.dom.removeAttribute('name');

            this.fileInput = this.wrap.createChild({
                id: this.getFileInputId(),
                name: this.name || this.getId(),
                cls: 'x-form-file',
                tag: 'input',
                type: 'file',
                size: 1
            });

            var btnCfg = Ext.applyIf(this.buttonCfg || {}, {
                text: this.buttonText
            });
            this.button = new Ext.Button(Ext.apply(btnCfg, {
                renderTo: this.wrap,
                cls: 'x-form-file-btn' + (btnCfg.iconCls ? ' x-btn-icon' : '')
            }));

            if (this.buttonOnly) {
                this.el.hide();
                this.wrap.setWidth(this.button.getEl().getWidth());
            }

            this.fileInput.on('change', function() {
                var v = this.fileInput.dom.value;
                this.setValue(v);
                this.fireEvent('fileselected', this, v);
            }, this);
        },

        // private
        getFileInputId: function() {
            return this.id + '-file';
        },

        // private
        onResize : function(width, h) {
            Ext.form.FileUploadField.superclass.onResize.call(this, width, h);

            this.wrap.setWidth(width);

            if (!this.buttonOnly) {
                width = this.wrap.getWidth() - this.button.getEl().getWidth() - this.buttonOffset;
                this.el.setWidth(width);
            }
        },

        // private
        preFocus : Ext.emptyFn,

        // private
        getResizeEl : function() {
            return this.wrap;
        },

        // private
        getPositionEl : function() {
            return this.wrap;
        },

        // private
        alignErrorIcon : function() {
            this.errorIcon.alignTo(this.wrap, 'tl-tr', [2, 0]);
        }

    });
    Ext.reg('fileuploadfield', Ext.form.FileUploadField);

    toolkit.plugins.WindowLoading = Ext.extend(
        Ext.Window,
        {
            constructor: function() {
                var cfg = {
                    width: 250,
                    closable: false,
                    draggable: false,
                    pbar: new Ext.ProgressBar({
                        text: "Um momento por favor.",
                        listeners: {
                            scope: this,
                            render: function() {
                                this.pbar.updateText("Aguardando negociação com servidor.");
                            }
                        }
                    }),
                    title: "Aguarde um momento",
                    listeners: {
                        scope: this,
                        render: function() {
                            this.add(this.pbar);
                            this.pbar.wait({
                                interval: 200,
                                duration: 5000,
                                increment: 10
                            })
                        }
                    }
                };

                toolkit.plugins.WindowLoading.superclass.constructor.call(this, cfg)
            }
        }
    );

    toolkit.plugins.XHtmlTextEditor = Ext.extend(
        Ext.form.HtmlEditor,
        {
            constructor: function(cf) {
                var defaults = {
                    enableColors: false,
                    enableFont: false,
                    enableLinks: false,
                    enableSourceEdit: toolkit.plugins.DEBUG_MODE
                };

                cf = Ext.apply(cf, defaults);

                if (cf.value == '' || cf.value == undefined)
                    cf.value = '<!-- Correção de bug da ExtJS -->';

                toolkit.plugins.XHtmlTextEditor.superclass.constructor.call(this, cf);
            }
        }
    );

    Ext.reg('xhtmleditor', toolkit.plugins.XHtmlTextEditor);

    toolkit.plugins.DateTimeField = Ext.extend(
        Ext.form.TextField,
        {
            constructor: function(cf) {
                if(!cf.value) cf.value = '';

                cf.defaults = {flex: 1.0};

                toolkit.plugins.DateTimeField.superclass.constructor.call(this, cf);
            },

            markInvalid: function(msg) {
                this.getDateField().markInvalid(msg);
                this.getTimeField().markInvalid(msg);
            },

            clearInvalid: function() {
                this.getDateField().clearInvalid();
                this.getTimeField().clearInvalid();
            },

            getDateField: function() {
                if(!this.dateField) {
                    this.dateField = new Ext.form.DateField({
                        value: this.value.split(' ')[0],
                        format: 'd/m/Y',
                        allowBlank: this.allowBlank,
                        submitValue: false,
                        listeners: {
                            scope: this,
                            change: function(field, newValue, oldValue) {
                                this._captureValue()
                            }
                        }
                    });
                }

                return this.dateField
            },

            _captureValue: function() {
                var value = this.getDateField().getRawValue() + ' ' + this.getTimeField().getValue();
                (this.getDateField().validate() && this.getTimeField()) && this.setValue(value);
            },

            getTimeField: function() {
                if(!this.timeField) {
                    this.timeField = new Ext.form.TextField({
                        value: this.value.split(' ')[1],
                        style: 'margin:0 5px',
                        xtype: 'textfield',
                        width: 70,
                        enableKeyEvents: true,
                        submitValue: false,
                        maxLength: 5,
                        allowBlank: this.allowBlank,
                        regex: /((0|1)[0-9]|2[0-3]):([0-5][0-9])/,
                        regexText: 'O horário informado é inválido, por favor corrija.',
                        listeners: {
                            scope: this,
                            keypress: function(field, event) {
                                if(event.getCharCode() >= 48 && event.getCharCode() <= 57) {
                                    field.getValue().length == 2 && field.setValue(field.getValue() + ':');
                                    field.getValue().length == 5 && event.stopEvent();
                                }
                                else if(event.getCharCode()  == 8) {
                                    field.getValue().length == 4 && field.setValue(field.getValue().substr(0, 3));
                                }
                                else if(  !(event.getCharCode() in toolkit.util.toIn([8, 9, 37, 38, 39, 40, 46])) ) {
                                    event.stopEvent()
                                }
                                else console.debug(event.getCharCode())
                            },
                            change: function(field, newValue, oldValue) {
                                this._captureValue()
                            },
                            blur: function(field) {
                                if(field.getValue() == '' && this.getDateField().getValue() != '')
                                    this.markInvalid('Você esqueceu de informar a hora.');
                            }
                        }
                    });
                }

                return this.timeField
            },

            setDateTime: function() {
                this.getDateField().setValue((new Date()).format('d/m/Y'));
                this.getTimeField().setValue((new Date()).format('H:i'));
                this._captureValue();
            },

            onRender: function(container, position) {
                var child = new Ext.Panel({
                    frame: false
                });

                new Ext.Panel({
                    border: false,
                    layout: 'hbox',
                    items: [
                        child,
                        this.getDateField(),
                        this.getTimeField(),
                        {
                            xtype: 'panel',
                            border: false,
                            style: 'margin: 0 8pt',
                            items: [
                                {
                                    xtype: 'button',
                                    icon: "/" + global.Context + "/static/images/chronometer.png",
                                    iconCls: true,
                                    handler: this.setDateTime,
                                    scope: this,
                                    tooltip: 'Preencher com horário atual.'
                                }
                            ]
                        }
                    ],
                    renderTo: container
                });

                toolkit.plugins.DateTimeField.superclass.onRender.call(this, child.body);
                this.hide();
            }
        }
    );

    Ext.reg('ndatetimefield', toolkit.plugins.DateTimeField);

    toolkit.plugins.ModelChoiceField = Ext.extend(
        Ext.form.ComboBox,
        {
            constructor: function(cf) {
                if(!cf.store) {
                    cf.store = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(cf.crudController, 'query'),
                        fields: ['pk', 'description'],
                        root: 'result'
                    });

                    cf.store.load({});
                }

                toolkit.plugins.ModelChoiceField.superclass.constructor.call(this, cf);
            }
        }
    );
    Ext.reg('modelchoicefield', toolkit.plugins.ModelChoiceField);

    toolkit.plugins.PasswordField = Ext.extend(
        Ext.form.TextField,
        {
            constructor: function(cf) {

                cf.hash = (Crypto.SHA1 ? { fn:Crypto.SHA1, name: 'sha1' } : {fn:Crypto.MD5, name: 'md5'});
                cf.listeners = {
                    scope: this,
                    blur: function() {
                        var crypt = '';
                        var salt = this.getSalt();

                        crypt = this.hash.name + '$' + salt + '$' + this.hash.fn(salt + this.getValue());
                        this.setValue(crypt);
                    },
                    focus: function() { this.setValue(''); }
                }

                toolkit.plugins.PasswordField.superclass.constructor.call(this, cf);
            },

            getSalt: function() {
                var chars = '0123456789abcdfghijlkmnopqrstuvxzy';
                var salt = '';
                var saltSize = 4 + (Math.floor(Math.random() * 2))

                while(salt.length < saltSize)
                    salt += chars.charAt(Math.floor(Math.random() * chars.length));

                return salt;
            },
        }
    );
    Ext.reg('passwordfield', toolkit.plugins.PasswordField);
}
