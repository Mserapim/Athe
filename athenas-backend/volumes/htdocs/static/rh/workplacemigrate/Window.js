Ext._define('rh.workplacemigrate.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.workplacemigrate.Restful',

    width: 600,
    height: 430,

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.oId = instance.pk;
                    this.action = 'update';
                    this._observe();
                }
            }
        });
        rh.workplacemigrate.Window.superclass.constructor.call(this, cfg);
        this._observe();
    },

    _observe: function () { },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Lotação',
                        allowBlank: false,
                        rest: 'rh.workplace.Restful',
                        name: 'workplace'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Lotação Destino',
                        allowBlank: true,
                        rest: 'rh.workplace.Restful',
                        name: 'workplace_destiny'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Publicação',
                        allowBlank: false,
                        rest: 'rh.publicacao.Restful',
                        name: 'publication'
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo',
                        allowBlank: false,
                        hiddenName: 'type_of_migrate',
                        choiceId: 'rh.TYPE_OF_MIGRATE'
                    },
                    {
                        fieldLabel: 'Descrição',
                        allowBlank: true,
                        name: 'description',
                        xtype: 'ckeditor',
                        height: 100
                    },
                ]
            });
        return this._formPanel;
    }
});

