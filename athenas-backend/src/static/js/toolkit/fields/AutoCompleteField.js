/**
 *
 **/

Ext.ns('toolkit.plugins');

toolkit.plugins.AutoCompleteField = Ext.extend(
    Ext.form.ComboBox,
    {
        setReadOnly: function(readOnly) {
            if(readOnly)
                this.button.disable();
            else
                this.button.enable();

            toolkit.plugins.AutoCompleteField2.superclass.setReadOnly.call(this, readOnly);
        },

        disable: function() {
            this.button.disable();
            toolkit.plugins.AutoCompleteField2.superclass.disable.call(this);
        },

        enable: function() {
            this.button.enable();
            toolkit.plugins.AutoCompleteField2.superclass.enable.call(this);
        },

        clearValue: function() {
            toolkit.plugins.AutoCompleteField2.superclass.clearValue.call(this);
            this.fireEvent('clear', this);
            this.focus();
        },

        setValue: function(value) {
            value = (value != '' ? value : null);

            if(value && (value != '' || value != null) && !(this.getStore().find(this.valueField, value) >= 0)) {
                this.getStore().baseParams.keyword = null;

                this.getStore().load({
                    params: { pk: value },
                    scope: this,
                    callback: function() {
                        var index = this.getStore().find(this.valueField, value);
                        if(index >= 0) {
                            var record = this.getStore().getAt(index);
                            record != undefined && this.fireEvent('select', this, record, index);
                            toolkit.plugins.AutoCompleteField2.superclass.setValue.call(this, value);
                            this.clearInvalid();
                        }
                        else {
                            this.markInvalid('Selecione um item da lista.');
                        }
                    }
                });
            }
            else if(value && value == '') {
                console.debug('do clear value');
            }
            else {
                toolkit.plugins.AutoCompleteField2.superclass.setValue.call(this, value);
            }
        },

        constructor: function(cf) {
            if(cf.crudController && !cf.father) {
                cf.store = new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action(cf.crudController, cf.queryAction),
                    fields: [
                        cf.valueField,
                        cf.displayField,
                        'controller'
                    ],
                    root: 'result'
                });
            }
            else if(cf.father) {
                //-- Correção para manter a compatibilidade com a versão anterior.
                cf.store = new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action(cf.father, 'autocomplete', [cf.model]),
                    fields: [
                        cf.valueField,
                        cf.displayField,
                        'controller'
                    ],
                    root: 'result'
                });
                cf.queryParam = 'query';
                //-- Correção para manter a compatibilidade com a versão anterior.
            }
            else if(cf.genericCrud) {
                cf.store = new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action('ExtCrudGeneric', 'query'),
                    fields: [
                        cf.valueField,
                        cf.displayField,
                        'controller'
                    ],
                    root: 'result',
                    baseParams: {
                        model_app_label: cf.model.app_label,
                        model_name: cf.model.name
                    }
                });
            };

            if(cf.defaultParams)
                Ext.apply(
                    cf.store.baseParams,
                    cf.defaultParams
                )

            cf.minChars = 3;

            Ext.applyIf(cf, {
                'resizable': true,
                'stateful': true,
                'stateId': 'stateful-' + this.controller + '-' + this.hiddenName
            });

            toolkit.plugins.AutoCompleteField2.superclass.constructor.call(this, cf);
            this.addEvents('clear');
        },

        _select: function() {
            var frm = new toolkit.plugins.AutocompleteSelectWindow(this);
            frm.show();
        },

        _edit: function() {
            if(this.getValue() != '') {
                var scope = {
                    father: {
                        controller: this.crudController,
                        reload_grid: function() {}
                    },
                    form: false
                };
                if(this.subcontrollers) {
                    var store = this.getStore();
                    scope.father.controller = store.getAt(store.find('pk', this.value)).get('controller');
                }
                scope.form = new toolkit.widget.ExtCrudForm(scope.father, 2, this.getValue());
                scope.form.action_commit_ex = scope.form.action_commit;
                scope.form.el = this;
                scope.form.action_commit = function(type) {
                    var r = this.action_commit_ex(type);
                    this.el.setValue(r.cid);
                    return r;
                };
                scope.form.show();
            }
            else alert('Nenhum item foi selecionado para edição.')
        },

        _add: function(specialized_controller) {
            var scope = {
                father: {
                    controller: this.crudController,
                    reload_grid: function() {}
                },
                form: false
            };

            if(specialized_controller)
                scope.father.controller = specialized_controller;

            scope.form = new toolkit.widget.ExtCrudForm(scope.father, 1);
            scope.form.action_commit_ex = scope.form.action_commit;
            scope.form.el = this;

            scope.form.action_commit = function(type) {
                var r = this.action_commit_ex(type);
                this.el.setValue(r.cid);
                return r;
            };

            scope.form.show();
        },

        onRender: function(container, position) {
            var child = new Ext.Panel({
                border: false
            });

            var menu = [
                {
                    text: 'Modificar',
                    icon: "/" + global.Context + '/static/images/edit.png',
                    scope: this,
                    handler: function() { this.clearValue(); }
                }
            ];

            if(this.conf) {
                (this.conf.canAdd || this.conf.canEdit) && menu.push('-');
                if(this.conf.canAdd && !this.subcontrollers)
                    menu.push({
                        text: this.conf.addLabel ? this.conf.addLabel : 'Adicionar ...',
                        icon: this.conf.addIcon ? this.conf.addIcon : '/' + global.Context + '/static/images/add.png',
                        scope: this,
                        handler: function() { this._add() }
                    });
                else if(this.conf.canAdd && this.subcontrollers) {
                    var submenu = [];

                    Ext.each(
                        this.subcontrollers,
                        function(record) {
                            submenu.push({
                                text: record.title,
                                icon: record.icon,
                                handler: function() { this._add(record.controller) },
                                scope: this
                            })
                        },
                        this
                    )

                    menu.push({
                        text: this.conf.addLabel ? this.conf.addLabel : 'Adicionar ...',
                        icon: this.conf.addIcon ? this.conf.addIcon : '/' + global.Context + '/static/images/add.png',
                        menu: submenu
                    });
                }

                if(this.conf.canEdit)
                    menu.push({
                        text: this.conf.editLabel ? this.conf.editLabel : 'Visualizar Registro ...',
                        icon: this.conf.editIcon ? this.conf.editIcon : '/' + global.Context + '/static/engine/images/icons/athenas-0036.png',
                        scope: this,
                        handler: this._edit
                    });
            }

            if(!this.genericCrud) {
                menu.push('-');
                menu.push({
                    text: 'Selecionar...',
                    scope: this,
                    handler: this._select,
                    scope: this,
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/document-export.png"
                });
            }

            var bnt = new Ext.Button({
                iconCls: true,
                style: 'margin-left: 5pt',
                icon: "/" + global.Context + "/static/images/view-sort-ascending.png",
                menu: menu
            });

            var panel = new Ext.Panel({
                layout: 'column',
                border: false,
                renderTo: container,
                cls: (this.toolbarInside ? 'toolbar-inside' : ''),
                items: [child, bnt]
            });

            this.button = bnt;

            this.width = this.width - (bnt.getBox().width + 5);

            toolkit.plugins.AutoCompleteField2.superclass.onRender.call(this, child.body);
        }
    }
);

//FIXME: Foi mantido para manter a compatibilidade.
toolkit.plugins.AutoCompleteField2 = toolkit.plugins.AutoCompleteField;

Ext.reg('autocompletefield', toolkit.plugins.AutoCompleteField2);