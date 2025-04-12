/**
 *
 **/
Ext._define('adm.patrimonio.baixa.ItemBaixaWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.baixa.ItemBaixaRestful',

    width: 650,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Patrimonio',
                        name: 'patrimonio',
                        rest: 'adm.patrimonio.PatrimonioRestful',
                        preFilter: [
                            {
                                property: 'item_entrada__nota__conta',
                                value: cfg.params.conta,
                                stage: 9998
                            },
                            {
                                property: 'data_tombo',
                                value: null,
                                stage: 9998
                            }
                        ],
                        gridConfig: {
                            gridAutoLoad: false
                        },
                    },
                    {
                        fieldLabel: 'Observações',
                        xtype: 'ckeditor',
                        name: 'observacao',
                        height: 200
                    }
                ]
            });

        return this._formPanel;
    }
});
