Ext._define('rh.gfp.estrutura_salarial.ReferenciaNiveis2DWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.estrutura_salarial.ReferenciaNiveis2DRestful',

    width: 600,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                // labelAlign: 'top',
                // title: 'Inner Tabs',
                bodyStyle:'padding:5px',
                // width: 800,
                items: [
                    Ext._create('core.fields.AutocompleteField', {
                        fieldLabel: 'Estrutura Salarial',
                        name: 'estrutura_salarial',
                        displayField: 'titulo',
                        allowBlank: false,
                        rest: 'rh.gfp.estrutura_salarial.EstruturaSalarialRestful',
                    }),{
                        fieldLabel: 'Ordem',
                        xtype: 'numberfield',
                        name: 'ordem',
                        allowBlank: false
                    },{
                        fieldLabel: 'Horizontal',
                        xtype: 'textfield',
                        name: 'horizontal',
                        allowBlank: true                        
                    },{
                        fieldLabel: 'Vertical',
                        xtype: 'textfield',
                        name: 'vertical',
                        allowBlank: true                        
                    },{
                        fieldLabel: 'Meses progressão',
                        xtype: 'numberfield',
                        name: 'months_progression',
                        allowBlank: false                        
                    },{
                        xtype: 'choicefield',
                        fieldLabel: 'Valor Servidor',
                        hiddenName: 'tipo_valor',
                        allowBlank: false,
                        name: 'tipo_valor',
                        choiceId: 'gfp.TYPE_OF_VALUE'
                    },{
                        xtype: 'choicefield',
                        choiceId: 'gfp.TYPE_OF_VALUE',
                        fieldLabel: 'Gratif. Servidor',
                        hiddenName: 'tipo_gratificacao',
                        name: 'tipo_gratificacao',
                        allowBlank: false,
                    },{
                        fieldLabel: 'Valor Membro',
                        xtype: 'choicefield',
                        choiceId: 'gfp.TYPE_OF_VALUE',
                        name: 'tipo_valor_membro',
                        hiddenName: 'tipo_valor_membro',
                        allowBlank: false,
                    },{
                        fieldLabel: 'Gratif. Membro',
                        xtype: 'choicefield',
                        choiceId: 'gfp.TYPE_OF_VALUE',
                        hiddenName: 'tipo_gratificacao_membro',
                        name: 'tipo_gratificacao_membro',
                        allowBlank: false,
                    },{
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Referência anterior",
                        allowBlank: true,
                        rest: "rh.gfp.estrutura_salarial.ReferenciaNiveis2DRestful",
                        name: "referencia_anterior"                        
                    },{
                        xtype:'numberfield',
                        fieldLabel: 'Fator de atualização',
                        name: 'fator_atualizacao',
                    }
                ],

            });

        return this._formPanel;
    },
});
