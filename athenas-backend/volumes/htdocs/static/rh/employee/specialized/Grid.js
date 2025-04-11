Ext._define('rh.employee.specialized.Grid', {
    extend: 'rh.employee.Grid',

    restWindow: 'rh.employee.specialized.Window',

    hideActions: ['copy', 'add', 'edit', 'remove'],
    configOrderToolBar: ['add', 'edit', '-', '-', 'search', '->', 'download'],

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        rh.employee.specialized.Grid.superclass.constructor.call(this, cfg);
        this.setManagerTab(cfg.managerTab);
    },

    setManagerTab: function(managerTab){
        if(this.managerTab == undefined)
            this.managerTab = managerTab;
    },

    getManagerTab: function(){
        return this.managerTab;
    },

    createItem: function(values) {
        this.getManagerTab().setTabPanel({
            oId: undefined,
            employeePk: undefined,
            employeeRegistry: undefined,
            naturalPersonPk: undefined,
            action: 'create'
        });
    },

    toggleFor: function(state, action) {
        var pkset = this.getSelectionModel().getSelections().map(function(data) {
            return data.get('pk');
        });
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});

        mask.show();
        rest.doRequest(
            rest.getRoute(
                action,
                false,
                'PUT',
                {
                    scope: this,
                    params: {
                        pk__in: pkset,
                        is_active: (state ? 'on': 'off')
                    },
                    callback: function() {
                        mask.hide();
                        mask = null;
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success){
                            Ext.Msg.show({
                                title: 'Ativando',
                                icon: Ext.Msg.OK,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                            this.getStore().reload();
                        }
                        else
                            Ext.Msg.show({
                                title: 'Ativando',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    },
                    failure: function(xhr) {
                        Ext.Msg.show({
                            title: 'Ativando',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso ainda processando requisição, tente novamente para confirmação de sucesso.'
                        });
                    }
                }
            )
        );
    },


    updateItem: function(record) {
        this._byUpdateClick = true;
        if(record instanceof Ext.Button)
            record = undefined;
        var selections = core.nullValue(record, this.getSelectionModel().getSelections());
        if(selections.length == 1){
            var selected = selections[0];
            this.getManagerTab().setTabPanel({
                oId: selected.get('pk'),
                employeePk: selected.get('pk'),
                employeeRegistry: selected.get('matricula'),
                naturalPersonPk: selected.get('naturalPersonPk'),
                is_member: selected.get('is_member'),
                action: 'update'
            });
        }else{
            Ext.Msg.show({
                title: 'Editando',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione apenas um item para edição.'
            });
        }
    },

    callUpdateEmployee: function(record, action) {
        if(this._byUpdateClick != true){
            if(record instanceof Ext.Button)
                record = undefined;

            var selected = core.nullValue(record, this.getSelectionModel().getSelected());

            if(action == 'create'){
                selected = undefined;
                record = undefined;
                this.getSelectionModel().clearSelections();
            }

            if(selected != undefined){
                this.getManagerTab().updateEmployeePanel(selected.get('pk'));
            }
        }else
            this._byUpdateClick = false;
    }
});

core.RestfulGrid.register(
    'rh.employee.specialized.Restful',
    'rh.employee.specialized.Grid'
);
