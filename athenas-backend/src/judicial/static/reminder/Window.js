Ext._define('judicial.reminder.Window', {
    extend: 'core.RestfulWindow',

    rest: 'judicial.reminder.Restful',

    width: 950,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'textfield',
                        allowBlank: false,
                        fieldLabel: 'Título',
                        name: 'title',
                        width: 815
                    },
                    {
                        name: "reminder_state",
                        fieldLabel: "Prioridade",
                        xtype: "combo",
                        allowBlank: false,
                        hiddenName: "reminder_state",
                        triggerAction: "all",
                        mode: "local",
                        store: [
                            [1,"Urgente"],
                            [2,"R\u00e1pido"],
                            [3,"Normal"]
                        ],
                        lazyRender: true
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Limitar o acesso',
                        items: [
                            {
                                xtype:'radiogroup',
                                columns: 3,
                                items: [
                                    {
                                        xtype:'radio',
                                        inputValue: 1,
                                        boxLabel: 'Para todo Ministério Público',
                                        checked: true,
                                        name: 'access_level'
                                    },
                                    {
                                        xtype:'radio',
                                        inputValue: 2,
                                        boxLabel: 'Para o departamento',
                                        checked: false,
                                        name: 'access_level'
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        xtype: 'container',
                        items: [
                            {
                                allowBlank: false,
                                name: "content",
                                xtype: "ckeditor",
                                height: 350
                            }
                        ]
                    }
                ]
            });

        return this._formPanel;
    }
});
