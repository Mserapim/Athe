Ext._define('rh.pvf.shiftmanager.DetailWindow', {
    extend: 'rh.pvf.portalrequest.DetailWindow',
    rest: 'rh.pvf.portalrequest.Restful',


    getFieldSet:function(cfg){
        return this.getDutyFieldSet(cfg)
    },


    getDutyFieldSet: function (cfg) {
        if (!this._duty)
            this._duty = Ext._create('Ext.form.FieldSet', {
                title: 'Plantões',
                items: [
                    this.getShitManagerGrid(cfg)
                ]
            });

        return this._duty;
    },

    getShitManagerGrid: function (cfg) {
        if (!this._shiftManagerGrid) {
            this._shiftManagerGrid = Ext._create('rh.pvf.shiftmanager.GridResume', {
                region: 'south',
                gridAutoLoad: false,
                height: 150,
                columnAction: false,
                columnLines: true,
                configOrderToolBar: [],
                //onlyColumns: ['start_date', 'end_date', 'days','type_activity'],
                canceledsFilterMenu:[],
                doubleClickHandler: function () { }
            });
            this._shiftManagerGrid.setFilterProperty('pk', cfg.data.duty_id);


        }
        return this._shiftManagerGrid;
    },

    getApproverButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [];
            if(!cfg.disableSave)
            if (cfg.data.approver_request){
                this._buttons.push(  
                    new Ext._create('Ext.Button', {
                        text: 'Confirmar realização do plantão',
                        hidden:cfg.data.buttons == 'approver_duty'?false:true,
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                        handler: function() { this.grantRequest(cfg) }
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Informar plantão não realizado',
                        iconCls: true,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'approver_duty'?false:true,
                        scope: this,
                        icon: '/' + global.Context + '/static/rh/images/pasu_nao_autorizado.png',
                        handler: function() {  this.rejectRequest(cfg)}
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Devolver ao Aprovador',
                        scope: this,
                        height:28,
                        with:32,
                        hidden:cfg.data.buttons == 'effective_duty'?false:true,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                        handler: function() { this.returnAppover(cfg)}
                            
                    }),
                    new Ext._create('Ext.Button', {
                        text: 'Efetivar',
                        hidden:cfg.data.buttons == 'effective_duty'?false:true,
                        scope: this,
                        height:28,
                        with:32,
                        iconCls: true,
                        icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                        handler: function() { this.effectiveRequest(cfg) }
                            
                    }),
                    
                )
            }
            return this._buttons;
        
        }
    },

    grantRequest: function (cfg) {
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
                approval_grid:cfg.approval_grid,
                detail_window:this,
                employee_grid:cfg.employee_grid,
                data: cfg.data,
                value:'defer',
                title: 'Confirmar',
        }).show();
        
    },

    rejectRequest:function(cfg){
        Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
            approval_grid:cfg.approval_grid,
            detail_window:this,
            employee_grid:cfg.employee_grid,
            data: cfg.data,
            value:'deny',
            title: 'Não Confirmar',
        }).show();
    },
    
    

});