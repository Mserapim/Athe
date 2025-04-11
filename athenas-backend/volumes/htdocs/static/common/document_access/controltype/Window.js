Ext._define('common.document_access.controltype.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.document_access.controltype.Restful',

    getLegalPrerogativeGrid: function(cfg) {
        if (!this._grid) {
            this._grid = Ext._create('common.document_access.legalprerogative.Grid', {
                gridAutoLoad: false,
                disabled: true,
                stripeRows: true,
                height: 300,
                hideColumns: [
                    'pk',
                    'unicode',
                    'control_type_unicode',
                    'created_by_unicode',
                    'created_at',
                    'modified_by_unicode',
                    'modified_at',
                ],
                viewConfig: {
                    scope: this,
                    getRowClass: function(record) {
                        if (record.data.enabled === false) {
                            return 'x-grid3-unabled';
                        }
                    }
                }
            });
        }

        return this._grid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'container',
                        layout: 'form',
                        labelWidth: 130,
                        items: [
                            {
                                fieldLabel: 'Título',
                                name: 'title',
                                xtype: "textfield",
                                allowBlank: false,
                                anchor: '99%',
                            },
                            {
                                name: "required_permission",
                                fieldLabel: "Permissão necessária",
                                xtype: "rest-autocompletefield",
                                allowBlank: false,
                                rest: "auth.PermissionRestful",
                                displayField: 'name',
                                preFilter: [
                                    { property: 'content_type__app_label', value: 'document_access', stage: 1000 },
                                    { property: 'codename__icontains', value: 'can_use_level_', stage: 1001 }
                                ]
                            }
                        ]
                    },
                    {
                        xtype: 'container',
                        layout: 'hbox',
                        defaults: {
                            xtype: 'container',
                            layout: 'form',
                            flex: 1,
                            labelWidth: 130,
                        },
                        items: [
                            {
                                flex: 1.0,
                                items: [
                                    {
                                        name: "max_period",
                                        fieldLabel: "Prazo máximo (anos)",
                                        xtype: "numberfield",
                                        allowBlank: false,
                                        width: '95%',
                                    },
                                    {
                                        name: "quantity",
                                        fieldLabel: "Pode aditar (vezes)",
                                        xtype: "numberfield",
                                        width: '95%',
                                    },
                                    {
                                        name: "weight",
                                        fieldLabel: "Ordenação",
                                        xtype: "numberfield",
                                        allowBlank: false,
                                        width: '95%',
                                    }
                                ]
                            },
                            {
                                labelWidth: 40,
                                flex: 1.0,
                                items: [
                                    {
                                        name: "is_secret",
                                        boxLabel: "Caracteriza documento Sigiloso",
                                        xtype: "checkbox",
                                        allowBlank: true
                                    },
                                    {
                                        name: "not_allow_admin_access",
                                        boxLabel: "Impede o acesso inclusive da comissão classificadora",
                                        xtype: "checkbox",
                                        allowBlank: true
                                    }
                                ]
                            },
                            {
                                labelWidth: 40,
                                flex: 0.5,
                                items: [
                                    {
                                        name: "enabled",
                                        boxLabel: "Habilitado",
                                        xtype: "checkbox",
                                        allowBlank: true,
                                    },
                                ]
                            }
                        ]
                    },
                    {
                        xtype: 'panel',
                        title: 'Hipóteses legais',
                        items: this.getLegalPrerogativeGrid(cfg),
                    },
                    {
                        // _TODO_ Is this a deprecated field?
                        xtype: 'container',
                        //height: 490,
                        items: [
                            {
                                name: "description",
                                //xtype: "ckeditor",
                                xtype: "textfield",
                                allowBlank: false,
                                value: 'deprecated field',
                                height: 380,
                                hidden: true,
                            }
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    objectId: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if (value !== undefined) {
            this.oId = value;

            if (dispatch) {
                this.objectIdObserve();
            }
        }

        return this.oId;
    },

    objectIdObserve: function() {
        if (this.oId) {
            this.getLegalPrerogativeGrid().setParam('control_type', this.oId);
            this.getLegalPrerogativeGrid().setFilterProperty('control_type', this.oId, 100);
            this.getLegalPrerogativeGrid().enable();
        } else {
            this.getLegalPrerogativeGrid().setParam('control_type', 0);
            this.getLegalPrerogativeGrid().setFilterProperty('control_type', 0, 100, false);
            this.getLegalPrerogativeGrid().getStore().removeAll();
            this.getLegalPrerogativeGrid().disable();
        }
    },

    saveAndContinueCallback: function (instance) {
        this.objectId(instance.pk);
        this.action = 'update';
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            saveAndContinue: {
                scope: this,
                fn: this.saveAndContinueCallback
            }
        });

        Ext.applyIf(cfg, {
            width: 900,
            autoHeight: true,
        });

        common.document_access.controltype.Window.superclass.constructor.call(this, cfg);
        this.objectId(this.oId);
    }
});
