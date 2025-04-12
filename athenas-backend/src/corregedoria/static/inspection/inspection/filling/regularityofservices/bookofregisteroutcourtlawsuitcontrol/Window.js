Ext._define('corregedoria.inspection.inspection.filling.regularityofservices.bookofregisteroutcourtlawsuitcontrol.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.regularityofservices.bookofregisteroutcourtlawsuitcontrol.Restful',

    width: 600,

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
                                labelWidth: 30,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        xtype: "textfield",
                                        fieldLabel: "Livro",
                                        name: "book",
                                        width: 240,
                                        allowBlank: false,
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 155,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Data do Termo de Abertura',
                                        name: 'opening_date',
                                        allowBlank: false,
                                        blankText: 'Data da Inspeção precisa ser preenchida.',
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
