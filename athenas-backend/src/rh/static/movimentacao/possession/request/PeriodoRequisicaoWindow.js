/**
 *
 **/
Ext._define('rh.movimentacao.possession.request.PeriodoRequisicaoWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.movimentacao.possession.request.PeriodoRequisicaoRestful',

    width: 550,

    tabHeight: 450,

    border: false,

    getFormPanel: function () {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                layout: 'form',
                frame: true,
                border: false,
                labelWidth: 140,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Publicação da requisição',
                        allowBlank: false,
                        rest: 'rh.publicacao.Restful',
                        name: 'publicacao',
                        width: 360
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
    },
});
