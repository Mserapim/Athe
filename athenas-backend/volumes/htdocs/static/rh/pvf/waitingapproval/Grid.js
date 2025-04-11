Ext._define('rh.pvf.waitingapproval.Grid', {
    extend: 'rh.pvf.portalrequest.Grid',
    //restWindow: 'rh.pvf.waitingapproval.Window',
    rest: 'rh.pvf.waitingapproval.Restful',

    configOrderToolBar: ['OpenRequest','-','search','LoadAll', '->', 'download'],

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(cfg, { gridAutoLoad: false });
        Ext.applyIf(cfg, {
            statusActivityMenu:this.setPreFilterStatus(cfg),
            typeEmployeeFilterMenu:this.setPreFilterEmployee(cfg)
        });
        rh.pvf.waitingapproval.Grid.superclass.constructor.call(this, cfg);
    },
    
    getColumnModel: function(cfg) {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Código', dataIndex: 'pk', width: 50},
                    {header: 'Descricao', dataIndex: 'unicode', id: 'autoExpandColumn',hidden:true},
                    {header: 'Data da Solicitação', dataIndex: 'date', width:120, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Tipo de Solicitação', dataIndex: 'type_of_request', width: 200},
                    {header: 'Servidor', dataIndex: 'employee_unicode', width: 250},
                    {header: 'Aprovador Atual',dataIndex:'custom_approver_current',width:150},
                    {header: 'Inicio', dataIndex: 'start_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y'),hidden:true},
                    {header: 'Fim', dataIndex: 'end_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y'),hidden:true}, 
                    {header: 'Dias Aguardando', dataIndex: 'days_awaiting_approval', width: 90},
                    {header: 'Situação', dataIndex: 'status_display', width: 250},
                ]
            );

        return this._columnModel;
    },

    defaultClickFunction: function(grid) {
        if(this.getSelectionModel().getSelected()) this.detail();
    },

    authorize_window: function () {
        if (!this.getSelectionModel().getSelected()) {
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione um item!'
            });
        } else {
            var selected = this.getSelectionModel().getSelected();
            Ext._create('rh.pvf.waitingapproval.DeferAndDenyWindow', {
                data: selected.data,
                title: 'Autorizar Solicitação',
            }).show();
        }
    },


    getOpenRequestAction:function(){
        return{
            text: 'Abrir Solicitação',
            scope: this,
            iconCls: true,
            icon: '/' + global.Context + '/static/rh/images/detalhes.png',
            handler: function () {
                this.detail()
            }
        }        
    },

    getLoadAllAction:function(){
        return{
            text: 'Atualizar Lista',
            scope: this,
            iconCls: true,
            icon: '/' + global.Context + '/static/rh/images/pasu_alterado.png',
            handler: function () {
                this.params.employee_grid.getSelectionModel().clearSelections()
                this.removeFilterProperty('employee');
                this.setFilterProperty('step_current__in',this.params.group_all,10045)
            }
        }        
    },
    
    detail: function (cfg) {
        if (!this.getSelectionModel().getSelected()) {
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione um item!'
            });
        } else {
            var selected = this.getSelectionModel().getSelected();
            Ext._create(selected.data.path_datail_window, {
                approval_grid:this.getStore(),
                employee_grid:this.params.employee_grid.getStore(),
                approver_flow:true,
                group_dgp:this.params.group_dgp,
                data: selected.data,
                status_hidden:this.params.status_hidden,
                group_progression:this.params.group_progression,
                action: 'update',
                title: 'Solicitação',
            }).show();
        }
    },

    getFilterMenu: function () {
        return [
            this.getApproverMenu(),
            this.getStatusActivityMenu(),
            this.getTypeEmployeeMenu(),
            this.getUsufructActivityMenu(),
            this.getLicenseActivityMenu(),
            this.getRequestTypeMenu(),
        ];
    },
});

core.RestfulGrid.register(
    'rh.pvf.waitingapproval.Restful',
    'rh.pvf.waitingapproval.Grid'
);   
