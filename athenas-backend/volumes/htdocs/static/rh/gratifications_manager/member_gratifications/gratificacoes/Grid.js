 Ext._define('rh.gratifications_manager.member_gratifications.gratificacoes.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gratifications_manager.member_gratifications.gratificacoes.Restful',

    restWindow: 'rh.gratifications_manager.member_gratifications.gratificacoes.Window',

    hideItemsToolbar: ['add','edit','remove','download'],
    hideActions: ['remove', 'copy', 'edit'],

    configOrderToolBar: ['search','->','btnAcaodeferirTodos','->'],

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            var itensTollBar = this.getConfigItemsToolbar(cfg);

            itensTollBar.splice(3, 0, '-');
            itensTollBar.splice(4, 0, '->');
            itensTollBar.splice(5, 0, this.btnAcaoDeferirTodos(cfg));
            itensTollBar.splice(6, 0, '-');
            
            

            this._toolbar = Ext._create('Ext.Toolbar', {
                style: cfg.toolbarStyle,
                items: itensTollBar,
            });

            if((this.toolbarHideLabel || cfg.toolbarHideLabel))
                this._toolbar.items.each(
                    function(item) {
                        item.tooltip = (item.tooltip || item.text);

                        if(item.text && core.nullValue(item.hideLabel, true))
                            item.text = null;
                    }
                );
        }

        return this._toolbar;
    },
    
    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true, id: 'autoExpandColumn'},
                    {header: '', dataIndex: 'icons', width: 75, menuDisabled: true, renderer: toolkit.util.formatStatus},
                    {header: 'Gratificação', dataIndex: 'evento_unicode', width: 350},
                    {header: 'Qtd Dias Consolidado', dataIndex: 'qtd_dias_consolidado', width: 120},
                    {header: 'Qtd Dias Deferido', dataIndex: 'qtd_dias_deferido', width: 120},
                    {header: 'Último Cálculo', dataIndex: 'data_ultimo_calculo', width: 110, hidden: true},
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
        return [
            {
                iconCls: 'icon-16px icon-fopag icon-compile',
                tooltip: 'Deferir',
                scope: this,
                handler: function(action, index){
                    var gratificacao = action._store.getAt(index).data
                    if(gratificacao.status == 'INDEFER'){
                        var msg = 'O registro selecionado está INDEFERIDO, tem certeza que deseja deferir?';
                    }else{
                        var msg = 'Tem certeza que deseja deferir o registro selecionado?';
                    }
                    

                    Ext.Msg.show({
                        msg: msg,
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        scope: this,
                        fn: function (b) {
                            if (b == 'no') return;

                            params = { 'gratificacao_id': gratificacao.pk };
                            this._realizarReq(params, 'GMGratificacoes', 'deferir_gratificacao_membro');
                        }
                    });
                },
            },
            {
                iconCls: 'icon-16px icon-core icon-core-delete',
                tooltip: 'Indeferir',
                scope: this,
                handler: function(action, index){
                    Ext.Msg.show({
                        msg: 'Tem certeza que deseja indeferir o registro selecionado?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        scope: this,
                        fn: function (b) {
                            if (b == 'no') return;

                            params = { 'gratificacao_id': action._store.getAt(index).data.pk };
                            this._realizarReq(params, 'GMGratificacoes', 'indeferir_gratificacao_membro');
                        }
                    });
                },
            },
        ];
    },


    btnAcaoDeferirTodos: function(cfg){
        return {
            text: 'Deferir Todos',
            iconCls: 'icon-16px icon-core icon-core-run',
            scope: this,
            handler: function(){ this.deferirTodosGratificacoes(cfg) },
        }
    },

    deferirTodosGratificacoes: function(cfg){
        var msg = 'Tem certeza que deseja calcular todos os registros do período selecionado? ';
        msg += 'Os registros Deferidos e Indeferidos serão ignorados.';
        
        var params = {
            'grat_membro_id': cfg.store.data.items[0].data.grat_membro_id,
        }

        Ext.Msg.show({
            msg: msg,
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                params = params;
                this._realizarReq(params, 'GMGratificacoes', 'deferir_todos_gratificacao_membro');
            }
        });
    },

});

core.RestfulGrid.register(
    'rh.gratifications_manager.member_gratifications.gratificacoes.Restful',
    'rh.gratifications_manager.member_gratifications.gratificacoes.Grid'
);
