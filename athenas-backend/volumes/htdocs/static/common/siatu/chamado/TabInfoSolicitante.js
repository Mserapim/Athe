/**
 *
 **/
Ext._define('common.siatu.chamado.TabInfoSolicitante', {
    extend: 'Ext.form.FormPanel',

     getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.Panel', {
                layout: 'form',
                frame: true,
                border: false,
                labelWidth:50,
                flex: 1.0,
                items: [
                    {
                        xtype: 'displayfield',
                        name: 'solicitante_nome',
                        fieldLabel: 'Nome'
                    },
                    {
                        xtype: 'displayfield',
                        name: 'solicitante_lotacao',
                        fieldLabel: 'Lotação'
                    },
                    {
                        xtype: 'displayfield',
                        name: 'solicitante_membro',
                        fieldLabel: 'Membro'
                    },
                    {
                        xtype: 'displayfield',
                        name: 'telefone',
                        fieldLabel: 'Telefone'
                    },
                    {
                        xtype: 'displayfield',
                        name: 'solicitante_cidade',
                        fieldLabel: 'Cidade'
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
            	title: 'Solicitante',
                layout: 'hbox',
                region:'south', 
                layoutConfig:{
                    align: 'stretch'
                },    
                items:[
                    this.getFormPanel()
                ]
            }
        );

        common.siatu.chamado.TabInfoSolicitante.superclass.constructor.call(this, cfg);
    }

});