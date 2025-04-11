Ext._define('corregedoria.inspection.inspection.filling.recommendations.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.recommendations.Restful',

    width: 1200,

    getEditor: function (cfg) {
        if (!this._ckeditoField) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, {
                allowBlank: true,
                startupFocus: false,
                editorConfig: {
                    forcePasteAsPlainText: true
                },
            });
            this._ckeditoField = Ext._create('toolkit.fields.CKEditor', cfg);
        }
        return this._ckeditoField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.8,
                                items: [
                                    this.getEditor({
                                        name: 'recommendation',
                                        width: 920,
                                        height: 350
                                    })
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.2,
                                items: [
                                    {
                                        xtype:'fieldset',
                                        title: 'Configurações',
                                        hideLabel: true,
                                        collapsible: false,
                                        autoHeight:true,
                                        width: 230,
                                        items: [
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                layout: 'form',
                                                labelWidth: 1,
                                                items: [
                                                    {
                                                        xtype: 'checkbox',
                                                        id: 'waiting_response',
                                                        name: 'waiting_response',
                                                        boxLabel: 'Aguarda retorno',
                                                        listeners: {
                                                            scope: this,
                                                            check: function(checkbox, checked){
                                                                if (checked) {
                                                                    this.getFormPanel().getForm().findField('deadline').enable();
                                                                } else {
                                                                    this.getFormPanel().getForm().findField('deadline').disable();
                                                                }
                                                            },
                                                            render: function(){
                                                                if (Ext.getCmp('waiting_response').checked) {
                                                                    this.getFormPanel().getForm().findField('deadline').enable();
                                                                } else {
                                                                    this.getFormPanel().getForm().findField('deadline').disable();
                                                                }
                                                            },
                                                        }
                                                    },
                                                ]
                                            },
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                layout: 'form',
                                                labelWidth: 40,
                                                style: {paddingLeft: '25px'},
                                                items: [
                                                    {
                                                        xtype: 'datefield',
                                                        fieldLabel: 'Prazo',
                                                        id: 'deadline',
                                                        name: 'deadline',
                                                        allowBlank: true,
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },

});
