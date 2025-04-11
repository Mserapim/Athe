/**
 *
 **/
Ext._define('rh.movimentacao.requisicao.EncargoFinanceiroWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.movimentacao.requisicao.EncargoFinanceiroRestful',

    tabHeight: 450,

    border: false,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                layout: 'form',
                frame: true,
                border: false,
                labelWidth: 140,
                items: [
                    {
                        fieldLabel: 'Remuneração',
                        xtype: 'numberfield',
                        name: 'remuneracao'
                    },
                    {
                        fieldLabel: 'Base Previdenciária',
                        xtype: 'numberfield',
                        name: 'base_previdenciaria'
                    },
                    {
                        fieldLabel: 'Data Início',
                        xtype: 'datefield',
                        name: 'data_inicio'
                    },
                    {
                        fieldLabel: 'Data Fim',
                        xtype: 'datefield',
                        name: 'data_fim'
                    }
                ]
            });

        return this._formPanel;
    }
});
