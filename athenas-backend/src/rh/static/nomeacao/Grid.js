Ext._define('rh.nomeacao.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.nomeacao.Window',

    configOrderToolBar: [
        'search',
    ],

    hideActions: ['add', 'edit', 'copy', 'remove', 'download'],

    getColumnModel: function(cfg) {
   
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', id: 'autoExpandColumn', hidden: true},
                    {header: 'Tipo Nomeação', dataIndex: 'tipo_nomeacao', width: 300},
                    {header: 'Provimento', dataIndex: 'provimento', width: 300},

                ]
            );

        return this._columnModel;
    },

    _realizarReq: function(params, nome_classe, nome_metodo){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(nome_classe,nome_metodo),
            params: params,
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
                if(obj.success == true){ this.getStore().reload(); }
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
    },

    getConfigCustomActions: function(){
        return [];
    },

});

core.RestfulGrid.register(
    'rh.nomeacao.Restful',
    'rh.nomeacao.Grid'
);