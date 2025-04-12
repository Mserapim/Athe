Ext._define('common.itop.userrequest.UserRequestWindow', {
    extend: 'Ext.Window',

    width: 550,
    height: 440,

    getDepartmentStore: function () {
        if (!this._departmentStore) {
            this._departmentStore = Ext._create('Ext.data.Store', {
                proxy: Ext._create('Ext.data.HttpProxy', {
                    url: core.callAction('CIUserRequest', 'work_locations_itop')
                }),
                reader: Ext._create('Ext.data.JsonReader', {
                    totalProperty: 'count',
                    root: 'collection',
                    fields: [
                        { name: 'pk', type: 'int' },
                        { name: 'description', type: 'string' },
                    ]
                }),
            });
        }

        return this._departmentStore;
    },

    getDepartmentField: function (cfg) {
        if (!this._departmentField) {
            this._departmentField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Lotação',
                hiddenName: 'general_organ',
                displayField: 'description',
                store: this.getDepartmentStore(),
                width: 500,
                allowBlank: true,
                listeners: {
                    scope: this,
                    afterrender: function () {
                        me = this;
                        this.getDepartmentStore().load({
                            callback: function (record) {
                                var general_organ_id = record[0].get('pk')
                                me.getDepartmentField().setValue(general_organ_id);
                                Ext.Ajax.request({
                                    url: core.callAction('CIUserRequest', 'get_location_phone'),
                                    params: {
                                        general_organ: general_organ_id
                                    },
                                    scope: me,
                                    success: function (response, options) {
                                        var obj = Ext.decode(response.responseText);
                                        me.getFormPanel().getForm().findField('phone').setValue(obj.location_phone)
                                    },
                                });
                            }
                        });
                    },
                    change: function () {
                        var general_organ_id = this.getDepartmentField().value
                        Ext.Ajax.request({
                            url: core.callAction('CIUserRequest', 'get_location_phone'),
                            params: {
                                general_organ: general_organ_id
                            },
                            scope: this,
                            success: function (response, options) {
                                var obj = Ext.decode(response.responseText);
                                this.getFormPanel().getForm().findField('phone').setValue(obj.location_phone)
                            },
                        });
                    }
                }
            });
        }

        return this._departmentField;
    },

    getEmployeeField: function () {
        if (!this._employeeField) {
            this._employeeField = Ext._create('Ext.form.DisplayField', {
                fieldLabel: 'Solicitante',
                xtype: 'displayfield',
                allowBlank: false,
                width: '350',
                name: 'user',
                listeners: {
                    scope: this,
                    render: function () {
                        Ext.Ajax.request({
                            url: core.callAction('CIUserRequest', 'get_logged_employee'),
                            scope: this,
                            success: function (response, options) {
                                var obj = Ext.decode(response.responseText);
                                this.getEmployeeField().setValue(obj.logged_employee_name)
                            },
                            failure: function (response, options) {
                                Ext.Msg.show({
                                    title: 'Servidor não encontrado.',
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK,
                                    msg: 'Não foi possível encontrar o solicitante. Tente novamente mais tarde.'
                                });
                            },
                        });
                    }
                }
            });
        }

        return this._employeeField;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelAlign: 'top',
                items: [
                    this.getEmployeeField(),
                    this.getDepartmentField(),
                    {
                        xtype: 'fonefield',
                        width: 220,
                        name: 'phone',
                        fieldLabel: 'Telefone',
                        allowBlank: false,
                    },
                    {
                        xtype: 'textarea',
                        width: 520,
                        height: 200,
                        name: 'description',
                        fieldLabel: 'Descrição',
                        allowBlank: false,
                    },
                ]
            });

        return this._formPanel;
    },

    save: function () {

        var values = this.getFormPanel().getForm().getValues()
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Salvando informações...' });
        mask.show();

        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('CIUserRequest', 'create_user_request'),
            params: {
                general_organ_id: values.general_organ,
                phone: values.phone,
                description: values.description
            },
            scope: this,
            success: function (request) {
                var obj = Ext.decode(request.responseText);
                if (obj.success === true) {
                    this.destroy();

                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK,
                        msg: obj.message
                    });
                } else {
                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: obj.message
                    });
                }
            },

            failure: function () {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Não foi possível registrar o chamado. Tente novamente mais tarde.'
                });
            },
            callback: function () { mask.hide(); },
        });
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Novo chamado'
        });

        Ext.apply(cfg, {
            items: [
                this.getFormPanel()
            ],
            buttons: [{
                text: 'salvar',
                scope: this,
                handler: function () { this.save() }
            },
            {
                text: 'Cancelar',
                scope: this,
                handler: this.destroy
            }
            ]
        });

        common.itop.userrequest.UserRequestWindow.superclass.constructor.call(this, cfg);
    },
});
