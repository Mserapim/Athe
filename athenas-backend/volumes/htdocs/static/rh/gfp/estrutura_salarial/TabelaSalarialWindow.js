Ext._define('rh.gfp.estrutura_salarial.TabelaSalarialWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.estrutura_salarial.TabelaSalarialRestful',

    width: 600,

    getItemsForm: function(cfg){
        items = [
            Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Estrutura Salarial',
                name: 'estrutura_salarial',
                displayField: 'unicode',
                allowBlank: false,
                rest: 'rh.gfp.estrutura_salarial.EstruturaSalarialRestful',
            }),
            Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Tabela anterior',
                name: 'tabela_anterior',
                displayField: 'unicode',
                allowBlank: true,
                useNull: true,
                rest: 'rh.gfp.estrutura_salarial.TabelaSalarialRestful',
            }),
            Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Publicação',
                name: 'publicacao',
                displayField: 'unicode',
                allowBlank: false,
                rest: 'rh.publicacao.Restful',
            }),{
                fieldLabel: 'Informação',
                xtype: 'textfield',
                name: 'info_adicional',
                allowBlank: true
            },{
                xtype:'datefield',
                fieldLabel: 'Início vigência',
                name: 'start_validity',
            },{
                xtype:'datefield',
                fieldLabel: 'Fim vigência',
                name: 'end_validity',
            },
        ];
        if(cfg.values['percentual'] != undefined){
            items.push({
                xtype:'numberfield',
                fieldLabel: 'Percentual (%)',
                name: 'percentual',
                allowBlank: false,
                allowNegative: false,

            });
            items.push({
                xtype:'hidden',
                name: 'copy',
                value: true
            });
        }

        return items;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                // labelAlign: 'top',
                // title: 'Inner Tabs',
                bodyStyle:'padding:5px',
                // width: 800,
                items: this.getItemsForm(cfg),

            });

        return this._formPanel;
    },
});
