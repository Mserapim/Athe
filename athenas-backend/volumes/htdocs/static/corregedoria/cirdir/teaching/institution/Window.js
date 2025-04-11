Ext._define('corregedoria.cirdir.teaching.institution.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.teaching.institution.Restful',

    width: 600,

    getCounty: function(cfg) {
        if(!this._county) {
            this._county = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Localidade',
                allowBlank: false,
                rest: "rh.localidade.Restful",
                name: "county",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                }
            });
        }
        return this._county;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        maxLength: 100,
                        allowBlank: false,
                        fieldLabel: 'Nome Fantasia',
                        name: 'nome',
                        xtype: 'textfield',
                        width: 450,
                    },
                    {
                        maxLength: 255,
                        allowBlank: false,
                        fieldLabel: 'Razão Social',
                        name: 'razao_social',
                        xtype: 'textfield',
                        width: 430
                    },
                    {
                        maxLength: 14,
                        allowBlank: false,
                        fieldLabel: 'CNPJ',
                        name: 'cnpj',
                        xtype: 'textfield',
                        width: 400
                    },
                    this.getCounty(cfg)
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {

        });
        corregedoria.cirdir.teaching.institution.Window.superclass.constructor.call(this, cfg);
    },

});
