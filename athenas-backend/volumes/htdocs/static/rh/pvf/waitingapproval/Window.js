Ext._define('rh.pvf.waitingapproval.Window', {
    extend: 'rh.pvf.portalrequest.Window',

    rest: 'rh.pvf.waitingapproval.Restful',


    getFormPanel: function(cfg) {
        //var selected = this.getSelectionModel().getSelected();
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [

                    {
                        title: 'Dados da Fruição',
                        xtype: 'fieldset',
                        items:[
                            {
                                xtype: 'hidden',
                                name: 'pk',
                                value: cfg.params.pk
                            },
                            {
                                name: "start_date",
                                fieldLabel: "Início",
                                xtype: "datefield",
                                allowBlank: false,
                                width:150,
                            },
                            {
                                name: "end_date",
                                fieldLabel: "Fim",
                                xtype: "datefield",
                                allowBlank: false,
                                width:150,
                            },
                        
                        ]
                    },
                   
                ]
            });

        return this._formPanel;
    },
    

});
