Ext._define('rh.lista_antiguidade_membros.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.lista_antiguidade_membros.Window',

    hideActions: ['add', 'remove', 'copy', 'edit'],

    configOrderToolBar: ['search', '->', 'download'],

    actionColumnWidth: 100,

    getColumnModel: function() {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: "Ordem Antiguidade", dataIndex: "ordem_antiguidade", sortable: true, width: 110},
                    {header: "Matrícula", dataIndex: "matricula", sortable: true, width: 80},
                    {header: "Nome", dataIndex: "nome", sortable: true, width: 200},
                    {header: "Tipo Membro", dataIndex: "tipo_cargo", sortable: true, width: 120},
                    {header: "Data Início Instância", dataIndex: "data_inicio_instancia", renderer: Ext.util.Format.dateRenderer('d/m/Y'), sortable: true, width: 120},
                    {header: "Data Início Carreira", dataIndex: "data_inicio_carreira", renderer: Ext.util.Format.dateRenderer('d/m/Y'), sortable: true, width: 120},
                    {header: "Tempo Afastamento", dataIndex: "tempo_afastamento_formatado", sortable: true, width: 120},
                    {header: "Tempo Total Instância", dataIndex: "total_instancia_formatado", sortable: true, width: 120},
                    {header: "Tempo Efetivo Exercício", dataIndex: "efetivo_exercicio_formatado", sortable: true, width: 120},
                    {header: "Tempo Total Carreira", dataIndex: "total_carreira_formatado", sortable: true, width: 120},
                    {header: "Posição Concurso", dataIndex: "posicao_concurso", sortable: true, width: 120},
                    {header: "Processado em", dataIndex: "modified_at", sortable: true, width: 120},
                    {header: "Origem", dataIndex: 'origem', sortable: true, id: 'autoExpandColumn', width: 150}
                ]
            );

        return this._columnModel;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            var itensTollBar = this.getConfigItemsToolbar(cfg);

            itensTollBar.splice(4, 0, '-');
            itensTollBar.splice(5, 0,
                    {
                        text: 'Filtro',
                        iconCls: 'icon-patrimonio icon-pat-filter',
                        menu: this.getFilterMenu(),
                    }
                );
            itensTollBar.splice(6, 0, '->');
            itensTollBar.splice(7, 0, this.btnAcaoAtualizaListaAntiguidades(cfg));




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

    setFilterEmpty: function(){
        this._configItemsToolbar.forEach(function(item, i){
            if(item.emptyText == 'Motor de buscas'){
                item.setValue('');
            }
        });

        this._toolbar.items.items.forEach(function(item, i){
            if(item.text == 'Filtro'){
                item.menu.items.items.forEach(function(item){
                    item.id == 'todos' ? item.setChecked(true) : item.setChecked(false);
                });
            }
        });
    },

    setParamsFilterMenu: function(chk, option){
        this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
            if(item.id != option ){
                item.setChecked(false);
            }
            if(!chk.checked == false && item.id == 'todos'){
                item.setChecked(true);
            }
        });
        if(option == 'procuradores' && !chk.checked == true){
            this.setFilterProperty('tipo_cargo', 1, true);
        }else if(option == 'promotores' && !chk.checked == true){
            this.setFilterProperty('tipo_cargo', 2, true);
        }else if(option == 'promotores_substitutos' && !chk.checked == true){
            this.setFilterProperty('tipo_cargo', 3, true);
        }else if(option == 'todos' && !chk.checked == true){
            this.removeFilterProperty('tipo_cargo', true);
        }
    },

    getFilterMenu: function(){
        this._getFilterMenu = [
            {
                id: 'todos',
                text: 'Todos',
                checked: true,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'todos') },
            },
            {
                id: 'procuradores',
                text: 'Procuradores',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'procuradores') },
            },
            {
                id: 'promotores',
                text: 'Promotores',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'promotores') },
            },
            {
                id: 'promotores_substitutos',
                text: 'Promotores Substitutos',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'promotores_substitutos') },
            },
        ];

        return this._getFilterMenu
    },

    constructor: function(cfg) {
        rh.lista_antiguidade_membros.Grid.superclass.constructor.call(this, cfg);
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

    btnAcaoAtualizaListaAntiguidades: function(cfg){
        return {
            text: 'Atualizar Lista de Antiguidades de Membros',
            iconCls: 'icon-16px icon-core icon-core-run',
            scope: this,
            handler: function(){ this.atualizarListaAntiguidades(cfg) },
        }
    },

    atualizarListaAntiguidades: function(cfg){
        var msg = 'Tem certeza que deseja atualizar a lista de antiguidades? '

         var params = {
            origem:'Manual'
        }

        Ext.Msg.show({
            msg: msg,
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;
                params=params
                this._realizarReq(params, 'ListaAntiguidadeRestfull', 'atualizar_lista_antiguidades_membros_manual');
            }
        });
    },
});

core.RestfulGrid.register(
    'rh.lista_antiguidade_membros.Restful',
    'rh.lista_antiguidade_membros.Grid'
);
