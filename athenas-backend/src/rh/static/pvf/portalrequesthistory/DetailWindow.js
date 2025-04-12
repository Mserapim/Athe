Ext._define('rh.pvf.portalrequesthistory.DetailWindow', {
    extend: 'Ext.Window',

    width: 700,

    height: 500,

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Detalhes',
                closable: true,
            }
        );
        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'fit',
                items: [
                    this.getFormPanel(cfg)
                ],
                buttons: this.getButtons(cfg),
            }
        );

        rh.pvf.portalrequesthistory.DetailWindow.superclass.constructor.call(this, cfg);
    },

    ret_annotation: function(cfg){       
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                'PortalRequestHistoryApi',
                'retificate_annotation'
            ),
            params: {
                pk: cfg.data.pk,
                obs: this.getFormPanel().getForm().getValues().observation,
            },
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                if(obj.success){
                    this.getFormPanel().getForm().setValues(this.values);
                    Ext.Msg.show({
                        title: 'Retificação de Anotação',
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK,
                        msg: obj.message
                    });
                    this.father.store.reload()
                }else
                    Ext.Msg.show({
                        title: 'Retificação de Anotação',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: obj.message
                    });
            },
            failure: function(e) {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                });
            },
            scope: this
        });
    },

    getReadOnlyObservation: function (cfg) {
        if (cfg.data.is_ascoger && cfg.data.group === 'mpmt-perfil-vdf-aprovador-assessoria-coger' ){
         return false
        }
        return true

    },

    getButtons: function (cfg) {
        if(!this._buttons) {
            this._buttons = [];
            if(!cfg.disableSave)
            if (cfg.data.is_ascoger && cfg.data.group === 'mpmt-perfil-vdf-aprovador-assessoria-coger' ){
                // 
                this._buttons.push(  
                    new Ext._create('Ext.Button', {
                        text: 'Retificar Anotação',
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                        handler: function() { 
                            Ext.Msg.show({
                                title:"Alterar Anotação",
                                icon: Ext.Msg.QUESTION,
                                buttons: Ext.Msg.YESNO,
                                msg: 'Deseja mesmo alterar a observação deste histórico ?',
                                scope: this,
                    
                                fn: function (btn) {
                                    if (btn == 'no') return;
                                    this.ret_annotation(cfg)
                                    
                                }
                            });
                        }
                    }),
                )          
            }
            this._buttons.push(        
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                },
        
            )
        }
        return this._buttons;
        
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        name: "date",
                        fieldLabel: "Data da a\u00e7\u00e3o",
                        xtype: "tk-datetimefield",
                        allowBlank: true,
                        value:cfg.data.date,
                        readOnly:true
                    },

                    {
                        name: "user_history",
                        fieldLabel: "Servidor",
                        xtype: "textfield",
                        allowBlank: true,
                        width:300,
                        maxLength: 255,
                        value:cfg.data.user_history,
                        readOnly:true
                    },
                    {
                        name: "group",
                        fieldLabel: "Grupo",
                        xtype: "textfield",
                        allowBlank: true,
                        width:300,
                        maxLength: 255,
                        value:cfg.data.group_name,
                        readOnly:true
                    },
                    {
                        fieldLabel: "Ação Realizada",
                        hiddenName: "action",
                        allowBlank: true,
                        width:300,
                        xtype: "choicefield",
                        choiceId: 'pvf.ACTION_TAKEN',
                        value:cfg.data.action,
                        readOnly:true
                    },

                    {
                        title: 'Observação:',
                        xtype: 'fieldset',
                        border: true,
                        items:[
                            {
                                name: "observation",
                                height:90,
                                width:650,
                                fieldLabel: "Observação",
                                value:cfg.data.observation,
                                readOnly: this.getReadOnlyObservation(cfg),
                                allowBlank: true,
                                hideLabel: true,
                                xtype: "textarea"
                            }
                        ]
                      
                    },
                   
                    // {
                    //     name: "observation",
                    //     //fieldLabel: "Observa\u00e7\u00e3o",
                    //     allowBlank: true,
                    //     hideLabel: true,
                    //     name: "texto",
                    //     xtype: "ckeditor",
                    //     value:cfg.data.observation,
                    //     readOnly:true
                    // }

                    
                ]

            });
        return this._formPanel;
    },

    

});