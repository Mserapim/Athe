 Ext._define('rh.gratifications_manager.member_gratifications.periodo.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gratifications_manager.member_gratifications.periodo.Restful',

    restWindow: 'rh.gratifications_manager.member_gratifications.periodo.Window',

    hideItemsToolbar: ['edit','search','download'],
    hideActions: ['remove', 'copy', 'edit'],

    configOrderToolBar: ['add',],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: 'Período', dataIndex: 'periodo', 'maxWidth': 200, id: 'autoExpandColumn'},
                    {header: 'Último Cálculo', dataIndex: 'data_ultimo_calculo', width: 120},
                ]
            );

        return this._columnModel;
    },

    _consolidarPeriodo: function(periodo_id){
        xt.Msg.show({
            msg: 'Tem certeza que deseja consolidar o período selecionado?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GMPeriodoGratMembros','consolidar_periodo'),
                    params: { periodo_id: periodo_id },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        var icon = obj.success == true ? Ext.Msg.INFO : Ext.Msg.ERROR;
                        Ext.Msg.show({
                            width:"400px",
                            title: this.title,
                            icon: icon,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                        this.getStore().reload();
                    },
                    failure: function() {
                        Ext.Msg.show({
                            title: this.title,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                        });
                    },
                    scope: this
                });
            }
        })
    },
    
    getConfigCustomActions: function(){
        return [
            {
                iconCls: 'icon-16px icon-core icon-core-run',
                tooltip: 'Consolidar',
                scope: this,
                handler: function(action, index){ this._consolidarPeriodo(action._store.getAt(index).data.pk) },
            },
        ];
    },

});

core.RestfulGrid.register(
    'rh.gratifications_manager.member_gratifications.periodo.Restful',
    'rh.gratifications_manager.member_gratifications.periodo.Grid'
);
