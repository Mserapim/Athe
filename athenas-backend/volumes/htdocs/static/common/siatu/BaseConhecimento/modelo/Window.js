/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.modelo.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.BaseConhecimento.modelo.Restful',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 60,
                items: [
                    {
                        xtype: 'textfield',
                        name: 'descricao',
                        fieldLabel: 'Descricao',
                        allowBlank: false,
                        width: 250,
                    },
                    {
                        xtype:'radiogroup',
                        fieldLabel: 'Área',
                        columns: 1,
                        items: [
                            {
                                xtype:'radio',
                                inputValue:'true',
                                boxLabel: 'Informática',
                                checked: this.values.informatica =='true',
                                name: 'informatica'
                            },
                            {
                                xtype:'radio',
                                inputValue:'false',
                                boxLabel: 'Administrativo',
                                checked: this.values.informatica =='false',
                                name: 'informatica'
                            },
                            {
                                xtype:'radio',
                                inputValue:'',
                                boxLabel: 'Ambos',
                                checked: this.values.informatica =='',
                                name: 'informatica'
                            }
                        ]
                    },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        if (cfg.action == 'update')
            this.values = cfg.values;
        else
            this.values = {informatica: ''};

        common.siatu.BaseConhecimento.modelo.Window.superclass.constructor.call(this, cfg);
    }
});
