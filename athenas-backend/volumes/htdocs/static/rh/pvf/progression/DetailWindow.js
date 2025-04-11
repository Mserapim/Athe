Ext._define('rh.pvf.progression.DetailWindow', {

    rest: 'rh.pvf.progression.Restful',
    extend:'rh.pvf.portalrequest.DetailWindow',

    height: 720,

    getTabPanel: function (cfg) {
        if (!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                tabPanelHeight: 620,
                height: 650,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    this.getManagerPanel(cfg),
                ]
            });

        return this._tabPanel;
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
                        ]
                    },
                    this.getFieldSet(cfg),
                    this.getTabHistory(cfg),
                    
                ]
            });
        return this._managementPanel;
    },

    getFieldSet:function(cfg){
        return this.getDocumentFieldSet(cfg)
    },

    getDocumentFieldSet: function (cfg) {
        if (!this._marked)
            this._marked = Ext._create('Ext.form.FieldSet', {
                title: 'Documentos',
                items: [
                    this.getDocumentGrid(cfg)
                ]
            });

        return this._marked;
    },

    getDocumentGrid: function(cfg) {
        if(!this._documentGrid) {
            this._documentGrid = Ext._create('rh.gfp.progression.document.Grid',{
                columnAction: false,
                region: 'center',
                height: 150,
                border: false,
                scope: this,
            });
        }
        this._documentGrid.setFilterProperty('progression__portal_request_progression__pk', cfg.data.pk)
        this._documentGrid.setParam('progression', cfg.data.progression);
        return this._documentGrid;
    },

    getApproverButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [];
            // if(!cfg.disableSave)
            if (cfg.data.approver_request){
                this._buttons.push( 
                    new Ext._create('Ext.Button', {
                        text: 'Devolver ao Solicitante',
                        scope: this,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'approver_point'?false:true,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                        handler: function() { this.returnApplicant(cfg)}
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Aprovar',
                        hidden:cfg.data.buttons == 'approver_point'?false:true,
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                        handler: function() { this.grantRequest(cfg) }
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Devolver ao Aprovador',
                        scope: this,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'effective_point'?false:true,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                        handler: function() { this.returnAppover(cfg)}
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Devolver ao Solicitante',
                        scope: this,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'effective_point'?false:true,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                        handler: function() { this.returnApplicant(cfg)}
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Efetivar',
                        hidden:cfg.data.buttons == 'effective_point'?false:true,
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                        handler: function() { this.effectiveRequest(cfg) }
                            
                    })
                    
                )
            }
               
        
        }
        
        return this._buttons;

    },

});
