Ext._define('rh.pvf.person.Window', {
    extend: 'rh.person.naturalperson.Window',
    //extend: 'core.RestfulWindow',

    rest: 'rh.pvf.person.Restful',
    height:465,
    width:600,


    _prepareSuccessCallback: function(callback, closeSuccess) {
        var wnd = this;

        callback = core.nullValue(callback, {});

        var success = core.nullValue(callback.success, {});
        var failure = core.nullValue(callback.failure, {});

        callback = core.nullValue(callback, {});

        function restoreCallbacks() {
            callback.success = success;
            callback.failure = failure;
        }

        callback.success = {
            fn: function(args) {
                core.invokeCallback(
                    (success || {fn: Ext.emptyFn}),
                    args
                );

                if(closeSuccess)
                    wnd.destroy();
                else
                    wnd.resetForm();

                restoreCallbacks();
            }
        };
        
        callback.failure = {
            scope: this,
            fn: function(args) {
                core.invokeCallback(
                    (failure || {fn: Ext.emptyFn}),
                    args
                );

                if(args.errors) {
                    var me = this;

                    args.errors.forEach(
                        function(error) {
                            var field = me.getFormPanel().getForm().findField(error.field);
                            if(field != undefined && field.xtype == 'rest-autocompletefield')
                                field = field.getComboField();

                            if(field) {
                                var tpl = new Ext.XTemplate(
                                    '<ul>',
                                    '<tpl for="values">',
                                    '<li>{.}</li>',
                                    '</tpl>',
                                    '</ul>'
                                );

                                field.markInvalid(tpl.apply(error));
                            }
                        }
                    );
                }

                restoreCallbacks();
            }
        };

        return callback;
    },


    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                width: 600,
                items: [
                    {
                        maxLength: 100,
                        allowBlank: false,
                        fieldLabel: 'Nome *',
                        name: 'nome',
                        xtype: 'textfield',
                        width:  424,
                    },
                    {
                        allowBlank: false,
                        fieldLabel: 'CPF *',
                        name: 'cpf',
                        xtype: 'cpffield',
                        width:  424
                    },
                    {
                        maxLength: 20,
                        allowBlank: true,
                        fieldLabel: 'RG *',
                        name: 'rg',
                        xtype: 'textfield',
                        width:  424
                    },

                    {
                        maxLength: 10,
                        allowBlank: true,
                        fieldLabel: 'RG Órgão *',
                        width:  424,
                        name: 'rg_orgao',
                        xtype: 'textfield',
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'RG UF *',
                        width:  424,
                        allowBlank: true,
                        rest: 'rh.estado.Restful',
                        name: 'rg_uf'

                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'RG Data Expedição *',
                        name: 'rg_data_expedicao',
                        xtype: 'datefield',
                        width:  424,

                    },
                    {
                        fieldLabel:'Data Nascimento *',
                        allowBlank: true,
                        name: 'data_nascimento',
                        xtype: 'datefield',
                        flex: 1,
                        width:  424,

                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Naturalidade *',
                        allowBlank: true,
                        rest: 'rh.localidade.Restful',
                        name: 'municipio_naturalidade',
                        width: 424
                    },
                    {
                        xtype: 'combo',
                        fieldLabel: 'Sexo *',
                        allowBlank: true,
                        lazyRender: true,
                        hiddenName: 'sexo',
                        mode: 'local',
                        triggerAction: 'all',
                        store: [
                            ['F', 'FEMININO'],
                            ['M', 'MASCULINO']
                        ],
                        name: 'sexo',
                        width: 424,
                    },
                    {
                        fieldLabel: 'Orientação Sexual',
                        xtype: 'choicefield',
                        hiddenName: 'sexual_orientation',
                        choiceId: 'rh.SEXUAL_ORIENTATION',
                        width: 424,
                    },
                    this.getImmigrantResidenceTimeField(cfg),
                    this.getImmigrantEntryConditionField(cfg)
                ]
            });

        return this._formPanel;
    }

});

// rh.pvf.person.Grid.register(
//     'rh.person.naturalperson.Window',
//     //'rh.pvf.person.Window'
// );    