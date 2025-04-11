 Ext._define('rh.gratifications_manager.member_gratifications.membros_consolidados.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gratifications_manager.member_gratifications.membros_consolidados.Restful',

    restWindow: 'rh.gratifications_manager.member_gratifications.membros_consolidados.Window',

    hideItemsToolbar: ['add','edit','remove','download'],
    hideActions: ['remove', 'copy', 'edit'],

    configOrderToolBar: ['search','->'],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true, id: 'autoExpandColumn'},
                    {header: '', dataIndex: 'icons', width: 30, menuDisabled: true, renderer: toolkit.util.formatStatus },
                    {header: 'Servidor', dataIndex: 'servidor_unicode', width: 150},
                    {header: 'Posse', dataIndex: 'data_posse', width: 75},
                    {header: 'Exercício', dataIndex: 'data_exercicio', width: 75},
                    {header: 'Desligamento', dataIndex: 'data_desligamento', width: 75},
                    {header: 'Afastamento', dataIndex: 'afastamento', width: 100},
                    {header: 'Cargo Efetivo', dataIndex: 'cargo_efetivo', width: 100},
                    {header: 'Cargo Comissão', dataIndex: 'cargo_comissao', width: 100},
                    {header: 'Cargo Eletivo', dataIndex: 'cargo_eletivo', width: 100},
                    {header: 'Último Cálculo', dataIndex: 'data_ultimo_calculo', width: 110},
                ]
            );

        return this._columnModel;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            var itensTollBar = this.getConfigItemsToolbar(cfg);

            itensTollBar.splice(2, 0, '-');

            var menuFiltroVerba = this.menuFiltroVerba(cfg);
            itensTollBar.splice(
                3,
                0,
                {
                    text: 'Filtrar Verba',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: menuFiltroVerba,
                }
            )

            itensTollBar.splice(4, 0, '-');

            var menuFiltroSituacao = this.menuFiltroSituacao(cfg);
            itensTollBar.splice(
                6,
                0,
                {
                    text: 'Filtro',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: menuFiltroSituacao,
                }
            )

            itensTollBar.splice(7, 0, '-');
                        
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

    menuFiltroVerbaItem: function(id,titulo,checked) {
        return {
            id: id,
            text: titulo,
            checked: checked,
            scope: this,
            hideOnClick: false,
            handler: function(chk) { this.filtrarVerba(chk, id) },
        }
    },

    menuFiltroVerba: function(cfg){
        var _menuFiltroStatus = [this.menuFiltroVerbaItem('0', 'Todos', true)];
        Ext.each(
            cfg.eventos,
            function(item) {
                _menuFiltroStatus.push(this.menuFiltroVerbaItem(item.numero, item.titulo, false));
            },
            this
        );

        return _menuFiltroStatus;
    },

    filtrarVerba: function(chk, opcao){
        var filtros_aplicar = [];
        if(opcao == '0'){
            if(!chk.checked == true){
                this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                    if(item.id != '0' && item.checked == true){
                        item.setChecked(false);
                    }
                });
            }else{
                this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                    if(item.id != '0' && item.checked == true){
                        filtros_aplicar.push(item.id);
                    }
                });
            }
        }else{
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.id == '0' && item.checked == true){
                    item.setChecked(false);
                }else if(
                    (item.id != '0' && item.id == opcao && !chk.checked == true) ||
                    (item.id != '0' && item.id != opcao && item.checked == true)
                ){
                    filtros_aplicar.push(item.id);
                }
            });
        }

        if(filtros_aplicar.length > 0){
            this.setFilterProperty('evento__numero__in', filtros_aplicar, 1, true);
            return true;
        }else{
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.id == '0' && !chk.checked == false){
                    item.setChecked(true);
                }
            });
            this.removeFilterProperty('evento__numero__in', 1, true);
        }
    },

    menuFiltroSituacaoItem: function(id, titulo, checked) {
        return {
            id: id,
            text: titulo,
            checked: checked,
            scope: this,
            hideOnClick: false,
            handler: function(chk) { this.filtrarSituacao(chk, id) },
        }
    },
 
    menuFiltroSituacao: function() {
        var _menuFiltroSituacao = [
            this.menuFiltroSituacaoItem('AVAL', 'Avaliar', true),
            this.menuFiltroSituacaoItem('DEFER', 'Deferido', false),
            this.menuFiltroSituacaoItem('INDEFER', 'Indeferido', false)
        ];
    
        return _menuFiltroSituacao;
    },

    filtrarSituacao: function(chk, opcao) {
       
        var filtros_aplicar = [];
        this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
            if(
                (item.id == opcao && !chk.checked) ||
                (item.id != opcao && item.checked)
            ){
                filtros_aplicar.push(item.id);
            }
        });
        if (filtros_aplicar.length == 0) {
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item) {
                if (item.id == 'AVAL') {
                    item.setChecked(true);
                    filtros_aplicar.push('AVAL');
                }
            });
        }
        if (filtros_aplicar.length > 0) {
            this.setFilterProperty('gratificacoes__status__in', filtros_aplicar, 3, true);
            return true;
        } else {
            this.removeFilterProperty('gratificacoes__status__in', 3, true);
        }
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
                iconCls: 'icon-16px icon-core icon-core-run',
                tooltip: 'Consolidar',
                scope: this,
                handler: function(action, index){
                    Ext.Msg.show({
                        msg: 'Tem certeza que deseja consolidar o registro selecionado?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        scope: this,
                        fn: function (b) {
                            if (b == 'no') return;

                            params = { 'grat_membro_id': action._store.getAt(index).data.pk };
                            this._realizarReq(params, 'GMGratMembros', 'consolidar_grat_membro_periodo');
                        }
                    });
                },
            },
        ];
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            gridAutoLoad: false,
        });

        rh.gratifications_manager.member_gratifications.membros_consolidados.Grid.superclass.constructor.call(this, cfg);
        this.setFilterProperty('gratificacoes__status__in', ['AVAL'], 3, true);
    },

});

core.RestfulGrid.register(
    'rh.gratifications_manager.member_gratifications.membros_consolidados.Restful',
    'rh.gratifications_manager.member_gratifications.membros_consolidados.Grid'
);
