Ext._define('edocs.protocolo.requestform.dependentexclusionitem.Window', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.protocolo.requestform.dependentexclusionitem.Restful',

    width: 900,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'fieldset',
                        title: 'Excluir',
                        items: [
                            {
                                name: "dependent",
                                fieldLabel: "Dependente",
                                xtype: "rest-autocompletefield",
                                allowBlank: false,
                                rest: "rh.dependent.byUser.Restful"
                            }
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Para fins de',
                        items: [
                            {
                                xtype: 'checkbox',
                                boxLabel: 'Imposto de Renda',
                                name: 'income_tax',
                                fieldLabel: '&nbsp;',
                                labelSeparator: '&nbsp;',
                                allowBlank: true,
                            },
                            {
                                xtype: 'checkbox',
                                boxLabel: 'Pensão Post Mortem',
                                name: 'post_mortem_pension',
                                fieldLabel: '&nbsp;',
                                labelSeparator: '&nbsp;',
                                allowBlank: true,
                            }
                        ]
                    }
                ]
            });

        return this._formPanel;
    }
});
