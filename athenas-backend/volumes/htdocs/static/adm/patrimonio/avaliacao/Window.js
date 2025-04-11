/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.Window', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.avaliacao.Restful',

    width: 390,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 150,
                items: [
                    {
                        fieldLabel: 'Tipo da avaliação',
                        xtype: 'combo',
                        hiddenName: 'tipo',
                        store: [
                            [ 1, 'DEPRECIAÇÃO DE ROTINA'],
                            [ 2, 'DEPRECIAÇÃO MANUAL'],
                            [ 3, 'REAVALIAÇÃO'],
                        ],
                        triggerAction: 'all'
                    },
                    {
                        fieldLabel: 'Mes da competencia',
                        xtype: 'combo',
                        hiddenName: 'mes',
                        store: [
                            [ 1, 'JANEIRO'],
                            [ 2, 'FEVEREIRO'],
                            [ 3, 'MARÇO'],
                            [ 4, 'ABRIL'],
                            [ 5, 'MAIO'],
                            [ 6, 'JUNHO'],
                            [ 7, 'JULHO'],
                            [ 8, 'AGOSTO'],
                            [ 9, 'SETEMBRO'],
                            [10, 'OUTUBRO'],
                            [11, 'NOVEMBRO'],
                            [12, 'DEZEMBRO'],
                        ],
                        triggerAction: 'all'
                    },
                    {
                        fieldLabel: 'Ano da competencia',
                        xtype: 'textfield',
                        name: 'ano'
                    },
                    {
                        fieldLabel: 'Apartir de',
                        name: 'de',
                        xtype: 'tk-datetimefield'
                    },
                    {
                        fieldLabel: 'Até',
                        name: 'ate',
                        xtype: 'tk-datetimefield'
                    }
                ]
            });

        return this._formPanel;
    }
});
