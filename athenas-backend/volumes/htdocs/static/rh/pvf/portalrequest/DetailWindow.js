Ext._define('rh.pvf.portalrequest.DetailWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.pvf.portalrequest.Restful',

    width: 720,
    
    height: 710,


    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: this.getTabPanel(cfg),
                submit_all_checks: true
            });

        return this._formPanel;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                tabPanelHeight: 600,
                height: 650,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    this.getManagerPanel(cfg),
                    this.getSubstitutePanel(cfg)
                    
                ]
            });

        return this._tabPanel;
    },


    getSubstitutePanel: function (cfg) {
        if (!this._substitutePanel)
            this._substitutePanel = Ext._create('Ext.Panel', {
                title: 'Substitutos',
                layout:"form",
                frame: true,
                border: false,
                height: 428,
                width:650,
                items: [

                    {
                        xtype: 'fieldset',
                        title: 'Substitutos',
                        layout:"form",
                        border: true,
                        items:[
                            this.getSubstituteFormPanel(cfg)
                        ]
                    }, 
                ]
            });

        if(cfg.data.has_substitute){
            this._substitutePanel.enable();
        }else{
            this._substitutePanel.disable();
        }
       

        return this._substitutePanel;
    },

    getSubstituteFormPanel: function (cfg) {
        if (!this._substituteGrid)
            this._substituteGrid = Ext._create('rh.pvf.portalrequestsubstitute.Grid', {
                region: 'center',
                disabled:cfg.action == "update"?false:true,
                columnAction: false,
                columnLines: true,
                configOrderToolBar: [],
                onlyColumns: ['start_date', 'end_date', 'substitute_unicode','exercise_unicode'],
                border: false,
                scope: this,
                doubleClickHandler: function () { },
                height: 120,
                columnAction: false,
            });
        this._substituteGrid.setFilterProperty('portal_request__pk', cfg.data.pk)
        return this._substituteGrid;
    },

    getManagerPanel: function (cfg) {
        if (!this._managementPanel)
            this._managementPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                title: 'Principal',
                layout: 'form',
                items: [
                    {
                        xtype: 'fieldset',
                        title: 'Informações:',
                        layout: 'column',
                        border: true,
                        items: [
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Data da solicitação: ',
                            },
                            {
                                columnWidth: cfg.data.acquisitive_period?.3:.8,
                                xtype: 'displayfield',
                                fieldLabel: 'Data da solicitação:',
                                style: {fontSize: '12px',marginBottom: '12px'},
                                value: Ext.util.Format.date(cfg.data.date, 'd/m/Y')
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Período Aquisitivo: ',
                                hidden:cfg.data.acquisitive_period?false:true,
                            },
                            {
                                columnWidth: .3,
                                fieldLabel: 'Período Aquisitivo',
                                xtype: 'displayfield',
                                style: {fontSize: '12px', marginBottom: '12px'},
                                value:cfg.data.acquisitive_period,
                                hidden:cfg.data.acquisitive_period?false:true,
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Tipo: ',
                            },
                            {
                                columnWidth: .8,
                                fieldLabel: 'Tipo',
                                style: {fontSize: '12px',marginBottom: '12px'},
                                xtype: 'displayfield',
                                value:cfg.data.type_of_request
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Solicitante: ',
                            },
                            {
                                columnWidth: .8,
                                fieldLabel: 'Solicitante',
                                style: {fontSize: '12px',marginBottom: '12px'},
                                xtype: 'displayfield',
                                value: cfg.data.employee_unicode
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                hidden:cfg.data.custom_approver_current?false:true,
                                value: 'Aprovador Atual: ',
                            },
                            {
                                fieldLabel: 'Aprovador Atual',
                                xtype: 'displayfield',
                                columnWidth: .8,
                                style: {fontSize: '12px',marginBottom: '12px'},
                                hidden:cfg.data.custom_approver_current?false:true,
                                value:cfg.data.custom_approver_current
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                value: 'Situação: ',
                            },
                            {
                                fieldLabel: 'Situação',
                                xtype: 'displayfield',
                                columnWidth: .8,
                                style: {fontSize: '12px',marginBottom: '12px'},
                                value:cfg.data.status_display
                            },
                            {
                                columnWidth: .2,
                                xtype: 'displayfield',
                                style: {fontSize: '12px'},
                                hidden:!cfg.data.parcel_number?true:false,
                                value: 'Nº Parcelas: ',
                            },
                            {
                                fieldLabel: 'Nº Parcelas',
                                xtype: 'displayfield',
                                columnWidth: .8,
                                style: {fontSize: '12px',marginBottom: '12px'},
                                hidden:!cfg.data.parcel_number?true:false,
                                value:cfg.data.parcel_number
                            },
                        ]
                    },
                    this.getFieldSet(cfg),
                    this.getTabHistory(cfg),
                ]
            });
        return this._managementPanel;
    },


    getHistoryGrid: function(cfg) {
        if(!this._historyGrid) {
            this._historyGrid = Ext._create('rh.pvf.portalrequesthistory.Grid',{
                hideItemsToolbar: ['remove', 'download','add','edit'],
                columnAction: false,
                allowCreate: false,
                allowRemove: false,
                allowUpdate: false,
                region: 'center',
                border: false,
                scope: this,
                height: 200,
                columnAction: false,
            });
        }
        this._historyGrid.setFilterProperty('portal_request', cfg.data.pk)
        return this._historyGrid;
    },

    getTabHistory: function(cfg) {
        if(!this._tabAddress)
            this._tabAddress = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Histórico',
                iconCls: '',
                border: false,
                frame: true,
                scope: this,
                autoHeight: true,
                items: [
                    this.getHistoryGrid(cfg)
                ]
            });
        return this._tabAddress;
    },

    getButtons: function (cfg) {
        if (cfg.approver_flow)
            return this.getApproverButtons(cfg)
        
    },

    getApproverButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [];
            if(!cfg.disableSave)
            if (cfg.data.approver_request){
                this._buttons.push(  
                    new Ext._create('Ext.Button', {
                        text: 'Deferir',
                        hidden:cfg.data.buttons == 'defer_deny'?false:true,
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                        handler: function() { this.grantRequest(cfg) }
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Efetivar‌',
                        hidden:cfg.data.buttons == 'effective'?false:true,
                        height:28,
                        with:32,
                        scope: this,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/pasu_fruido.png',
                        handler: function() { this.effectiveRequest(cfg) }
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Indeferir',
                        iconCls: true,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'defer_deny'?false:true,
                        scope: this,
                        icon: '/' + global.Context + '/static/rh/images/pasu_nao_autorizado.png',
                        handler: function() {  this.rejectRequest(cfg)}
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Confirmar Ciência',
                        scope: this,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'science'?false:true,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/core/publication-confirmed.png',
                        handler: function(){this.confirmScience(cfg)}
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Anotar',
                        scope: this,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'annotation'?false:true,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                        handler: function() { this.annotation(cfg)}
                            
                    })
                )
            }
               
        
        }

        if(cfg.status_hidden.includes(cfg.data.status)){
            this._buttons = []
        }else{
            if(!cfg.data.approver_request && cfg.group_dgp){
                this._buttons = [
                    new Ext._create('Ext.Button', {
                        text: 'Anotar',
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                        handler: function() { this.dgp_observation(cfg)}
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Cancelar Solicitação',
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/denied.png',
                        handler: function() { this.cancel(cfg)}
                            
                    })
                ] 
            
            }else if(cfg.data.approver_request && cfg.group_dgp){
                this._buttons.push(
                    new Ext._create('Ext.Button', {
                        text: 'Anotar',
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                        handler: function() { this.dgp_observation(cfg)}
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Cancelar Solicitação',
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/denied.png',
                        handler: function() { this.cancel(cfg)}
                            
                    })
                )
            }
        }
        return this._buttons;

    },

    grantRequest: function (cfg) {
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
                approval_grid:cfg.approval_grid,
                detail_window:this,
                employee_grid:cfg.employee_grid,
                data: cfg.data,
                value:'defer',
                title: 'Deferir',
        }).show();
        
    },

    effectiveRequest: function (cfg) {
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
                approval_grid:cfg.approval_grid,
                detail_window:this,
                employee_grid:cfg.employee_grid,
                data: cfg.data,
                value:'defer',
                title: 'Efetivar',
        }).show();
        
    },

    rejectRequest:function(cfg){
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
            approval_grid:cfg.approval_grid,
            detail_window:this,
            employee_grid:cfg.employee_grid,
            data: cfg.data,
            value:'deny',
            title: 'Indeferir',
        }).show();
    },

    confirmScience:function(cfg){
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
            approval_grid:cfg.approval_grid,
            detail_window:this,
            employee_grid:cfg.employee_grid,
            data: cfg.data,
            value:'science',
            title: 'Confirmar Ciência',
        }).show();
    },

    annotation:function(cfg){
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
            approval_grid:cfg.approval_grid,
            detail_window:this,
            employee_grid:cfg.employee_grid,
            data: cfg.data,
            value:'annotation',
            title: 'Anotação',
        }).show();
    },
    dgp_observation:function(cfg){
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
            approval_grid:cfg.approval_grid,
            detail_window:this,
            employee_grid:cfg.employee_grid,
            data: cfg.data,
            value:'dgp_observation',
            title: 'Anotação',
        }).show();
    },
    returnApplicant:function(cfg){
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
            approval_grid:cfg.approval_grid,
            detail_window:this,
            employee_grid:cfg.employee_grid,
            data: cfg.data,
            value:'return_applicant',
            title: 'Devolver ao Solicitante',
        }).show();
    },
    returnAppover:function(cfg){
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
            approval_grid:cfg.approval_grid,
            detail_window:this,
            employee_grid:cfg.employee_grid,
            data: cfg.data,
            value:'return_approver',
            title: 'Devolver ao Aprovador',
        }).show();
    },
    cancel:function(cfg){
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
            approval_grid:cfg.approval_grid,
            detail_window:this,
            employee_grid:cfg.employee_grid,
            data: cfg.data,
            value:'cancel',
            title: 'Cancelar',
        }).show();
    }

});