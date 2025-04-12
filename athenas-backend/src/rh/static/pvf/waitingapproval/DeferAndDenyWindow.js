Ext._define('rh.pvf.waitingapproval.DeferAndDenyWindow', {
    //extend: 'rh.pvf.portalrequest.Window',
    extend: 'core.RestfulWindow',

    rest: 'rh.pvf.waitingapproval.Restful',
    
    width:600,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [

                    {
                        title: 'Informe a Publicação',
                        xtype: 'fieldset',
                        hidden:cfg.data.is_awaiting_completion?cfg.value == "defer"?false:true:true,
                        border: true,
                        items:[
                            {
                                xtype: 'rest-autocompletefield',
                                fieldLabel: 'Publicação',
                                allowBlank: true,
                                rest: 'rh.publicacao.Restful',
                                name: 'publication',
                            }  
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Adicionar documento:',
                        hidden:cfg.data.is_awaiting_completion_prog_h?cfg.value == "defer"?false:cfg.value == "deny"?false:true:true,                        
                        border: true,
                        items: [
                            this.getDocumentButton(cfg),
                            {
                                fieldLabel: 'Informação',
                                xtype: 'displayfield',
                                value: 'Para visualizar os documentos cadastrados, atualize a lista de documentos na tela anterior!'
                            },
                        ]
                    },
                    {
                        title: 'Observação (opcional)',
                        xtype: 'fieldset',
                        border: true,
                        items:[
                            {
                                fieldLabel: "Observação (opcional)",
                                allowBlank: true,
                                hideLabel: true,
                                height:100,
                                width:550,
                                name: "texto",
                                xtype: "textarea"
        
                            }
                        ]
                    }, 
                   
                ]
            });

        return this._formPanel;
    },

    getDocumentButton: function(cfg) {
        this._generateButton = Ext._create('Ext.Button', {
            text: 'Adicionar anexo',
            scope: this,
            height:20,
            columnWidth: .2,
            iconCls: 'icon-ged icon-ged-application-pdf',
            handler: function() { this._getDocumentWindow(cfg) }
            
        });

        return this._generateButton;
    },

    _getDocumentWindow: function(cfg){
        new rh.pvf.progression_h.document.Window({
            title: 'Adicionar documento',
            action: 'create',
            params: {pr_progression_h: cfg.data.pk},
        }).show();
    },

    getButtons: function (cfg) {
        if (!this._buttons) {
            this._buttons = [];

            this._buttons.push({
                text: 'Confirmar',
                scope: this,
                handler: function () {
                    if(cfg.value == "cancel"){
                        Ext.Msg.show({
                            title:"Cancelar",
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            msg: 'Deseja mesmo cancelar a solicitação?',
                            scope: this,
                
                            fn: function (btn) {
                                if (btn == 'no') return;
                                this.authorize(cfg)
                            }
                        });
                    }else{
                        this.authorize(cfg)
                    }
                   
                }
            });

            this._buttons.push({
                text: 'Fechar',
                scope: this,
                handler: this.destroy
            });
        }
        return this._buttons;
    },    

    authorize: function(cfg){
        var rest = this.factoryRestful();
        var params = this.getFormPanel().getForm().getValues()
        request_grid =  Ext._create('rh.pvf.waitingapproval.Grid', {});
        employee_grid= Ext._create('rh.employee.Grid',{});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});
        mask.show();
        rest.doRequest(
            rest.getRoute('authorize_request', false, 'POST', {
                scope: this,
                params: {
                    pk:cfg.data.pk,
                    action:cfg.value,
                    observation:params.texto,
                    publication:params.publication
                },
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        this.destroy();
                        cfg.detail_window.destroy()
                        //cfg.employee_grid.reload()
                        cfg.approval_grid.reload()
                    
                    }
                    else
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                    },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Atenção',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        );
    },

});
