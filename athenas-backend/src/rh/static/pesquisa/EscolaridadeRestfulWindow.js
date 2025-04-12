/**
 *
 **/
Ext._define('rh.pesquisa.EscolaridadeRestfulWindow', {
    'extend': 'core.RestfulWindow',

    'rest': 'rh.pesquisa.EscolaridadeRestful',
    width:500,
    'getFormPanel': function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                'frame': true,
                'border': false,
                'defaults': {
                    'width': 350
                },
                'items': [
                   {
                       xtype: 'combo',
                       hiddenName: 'nivel_escolaridade',
                       fieldLabel: 'Nível de Escolaridade',
                       store: [
                           [1, 'MÉDIO'],
                           [2, 'TÉCNICO'],
                           [3, 'SUPERIOR'],
                           [4, 'PÓS-GRADUAÇÃO'],
                           [5, 'MESTRADO'],
                           [6, 'DOUTORADO'],
                           [7, 'PÓS-DOUTORADO'],
                       ],
                       triggerAction: 'all',
                   },
                   {
                       fieldLabel: 'Instituição de Ensino',
                       xtype: 'textfield',
                       allowBlank: true,
                       name: 'instituicao'
                   },
                   {
                       fieldLabel: 'Curso',
                       xtype: 'textfield',
                       allowBlank: true,
                       name: 'curso'
                   },
                   {
                       fieldLabel: 'Ano de Conclusão',
                       xtype: 'numberfield',
                       allowBlank: true,
                       name: 'ano_conclusao'
                   },
                   {
                       displayField: 'description', 
                       name:'cidade',
                       fieldLabel: 'Cidade', 
                       allowBlank: true, 
                       hiddenName: 'cidade', 
                       valueField: 'pk', 
                       triggerAction: 'all', 
                       queryAction: 'query', 
                       hideTrigger: true, 
                       queryParam: 'keyword', 
                       crudController: 'RHLocalidade', 
                       xtype: 'autocompletefield',
                   }
                ]
            });

        return this._formPanel;
    }
});
