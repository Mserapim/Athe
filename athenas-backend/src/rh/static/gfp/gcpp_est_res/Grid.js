 Ext._define('rh.gfp.gcpp_est_res.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.gcpp_est_res.Window',

    configOrderToolBar: [
        'search',
        'download'
    ],

    hideActions: ['add', 'edit', 'remove', 'copy'],

    actionColumnWidth: 100,

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 60, hidden: true, id: 'autoExpandColumn'},
                    {header: '', dataIndex: 'icons', sortable: true, width: 50, menuDisabled: true, renderer: toolkit.util.formatStatus },
                    {header: 'Servidor', dataIndex: 'servidor_unicode', width: 250},
                    {header: 'Verba', dataIndex: 'verba', width: 250},
                    {header: 'Qtd Dias Confirmado', dataIndex: 'qtd_dias_confirmado', width: 100},
                    {header: 'Qtd Dias Calculado', dataIndex: 'qtd_dias_calculado', width: 100},
                    {header: 'Valor Calculado', dataIndex: 'valor_calculado', width: 90, renderer: toolkit.util.formatCurrency},
                    {header: 'Qtd Dias p/ Pgto', dataIndex: 'qtd_dias_pgto', width: 100},
                    {header: 'Valor p/ Pgto', dataIndex: 'valor_pgto', width: 100, renderer: toolkit.util.formatCurrency},
                    {header: '% Deferida', dataIndex: 'pct', width: 80, renderer: toolkit.util.formatCurrency},
                    {header: 'Ref. da Falta', dataIndex: 'ref_falta', width: 90},
                    {header: 'Período Ref.', dataIndex: 'periodo', width: 100},
                    {header: 'Data Conferência', dataIndex: 'conferido_em', width: 100},
                    {header: 'Conferido Por', dataIndex: 'conferido_por', width: 250, hidden: true},
                    {header: 'Modificado Por', dataIndex: 'modified_by_unicode', width: 250, hidden: true},
                ]
            );

        return this._columnModel;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            var itensTollBar = this.getConfigItemsToolbar(cfg);

            var menuAcoes = this.menuAcoes();
            itensTollBar.splice(
                0,
                0,
                {
                    text: 'Ações',
                    iconCls: 'icon-16px icon-fopag icon-node-select',
                    menu: menuAcoes,
                }
            )
            itensTollBar.splice(1, 0, '-');
            itensTollBar.splice(2, 0, '->');
            itensTollBar.splice(3, 0, 'Ano: ');
            itensTollBar.splice(4, 0, this.comboAno());
            itensTollBar.splice(5, 0, '-');
            itensTollBar.splice(6, 0, 'Mês: ');
            itensTollBar.splice(7, 0, this.comboMes());
            itensTollBar.splice(8, 0, '-');
            itensTollBar.splice(9, 0, 'Tipo: ');
            itensTollBar.splice(10, 0, this.comboTipo());

            var menuFiltroStatus = this.menuFiltroStatus();
            itensTollBar.splice(
                15,
                0,
                {
                    text: 'Filtrar Status',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: menuFiltroStatus,
                }
            )

            var menuFiltroVerba = this.menuFiltroVerba(cfg);
            itensTollBar.splice(
                16,
                0,
                {
                    text: 'Filtrar Verba',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: menuFiltroVerba,
                }
            )
                        
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

    menuFiltroStatusItem: function(id, texto, checked){
        return {
            id: id,
            text: texto,
            checked: checked,
            scope: this,
            hideOnClick: false,
            handler: function(chk) { this.filtrarStatus(chk, id) },
        }
    },

    menuFiltroStatus: function(){
        var _menuFiltroStatus = [
            this.menuFiltroStatusItem('todos', 'Todos', true),
            this.menuFiltroStatusItem('analise', 'Em Análise para Pgto', false),
            this.menuFiltroStatusItem('apto', 'Aptos a Pgto', false),
            this.menuFiltroStatusItem('pago', 'Pagos', false),
            this.menuFiltroStatusItem('inapto', 'Inaptos', false),
        ];

        return _menuFiltroStatus;
    },

    filtrarStatus: function(chk, opcao){
        var filtros_aplicar = [];
        if(opcao == 'todos'){
            if(!chk.checked == true){
                this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                    if(item.id != 'todos' && item.checked == true){
                        item.setChecked(false);
                    }
                });
            }else{
                this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                    if(item.id != 'todos' && item.checked == true){
                        filtros_aplicar.push(item.id);
                    }
                });
                if(filtros_aplicar.length == 0){
                    filtros_aplicar.push('analise');
                    this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                        if(item.id == 'analise'){ item.setChecked(true); }
                    });
                }
            }
        }else{
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.id == 'todos' && item.checked == true){
                    item.setChecked(false);
                }else if(
                    (item.id != 'todos' && item.id == opcao && !chk.checked == true) ||
                    (item.id != 'todos' && item.id != opcao && item.checked == true)
                ){
                    filtros_aplicar.push(item.id);
                }
            });
        }

        if(filtros_aplicar.length > 0){
            this.setFilterProperty('status__in', filtros_aplicar, 4, true);
        }else{
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.id == 'todos' && !chk.checked == false){
                    item.setChecked(true);
                }
            });
            this.removeFilterProperty('status__in', 4, true);
        }
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
            cfg.verbas,
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
            this.setFilterProperty('evento__numero__in', filtros_aplicar, 5, true);
        }else{
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.id == '0' && !chk.checked == false){
                    item.setChecked(true);
                }
            });
            this.removeFilterProperty('evento__numero__in', 5, true);
        }
    },

    exibirMsgErro: function(msg){
        Ext.Msg.show({
            minWidth: 400,
            title: this.title,
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK,
            msg: msg
        });
    },

    calcConfDeclAplicGcpp: function(nome_metodo, tipo_calculo, gcpp_id=0){
        var msg_erro = '';
        var msg_pergunta = '';
        var params = '';

        var filtro_ano = '';
        var filtro_mes = '';
        var filtro_txt = '';
        var filtro_status = [];
        var filtro_verba = [];
        this._toolbar.items.items.forEach(function(item, i){
            if(item.emptyText == 'Ano para filtro'){ filtro_ano = item.getValue(); }
            if(item.emptyText == 'Mês para filtro'){ filtro_mes = item.getValue(); }
            if(item.emptyText == 'Motor de buscas'){ filtro_txt = item.getValue(); }

            if(item.text == 'Filtrar Status'){
                item.menu.items.items.forEach(function(item_filtro){
                    if(item_filtro.id != 'todos' && item_filtro.checked == true){ filtro_status.push(item_filtro.id); }
                });
            }

            if(item.text == 'Filtrar Verba'){
                item.menu.items.items.forEach(function(item_filtro){
                    if(item_filtro.id != '0' && item_filtro.checked == true){ filtro_verba.push(item_filtro.id); }
                });
            }
        });

        if(tipo_calculo == 'unico'){
            params = { gcpp_ids: [gcpp_id] };
            msg_pergunta = 'Tem certeza que deseja '+nome_metodo.split('_')[0]+' o registro selecionado?';
        }else if(tipo_calculo == 'selecionados'){
            var selecionados = this.getSelectionModel().getSelections().map(function(a){ return a.id; });

            if(selecionados.length == 0){
                msg_erro = 'Escolha pelo menos um registro para '+nome_metodo.split('_')[0]+'.';
            }else{
                params = { gcpp_ids: selecionados };
                msg_pergunta = 'Tem certeza que deseja '+nome_metodo.split('_')[0]+' os registros selecionados?';
            }
        }else if(tipo_calculo == 'todos'){
            params = {
                gcpp_ids: 'todos',
            };
            msg_pergunta = 'Tem certeza que deseja '+nome_metodo.split('_')[0]+' todos os registros?';
        }

        params['filtro_ano'] = filtro_ano;
        params['filtro_mes'] = filtro_mes;
        params['filtro_txt'] = filtro_txt;
        params['filtro_status'] = filtro_status;
        params['filtro_verba'] = filtro_verba;

        if(msg_erro != ''){
            this.exibirMsgErro(msg_erro);
        }else{
            Ext.Msg.show({
                msg: msg_pergunta,
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (b) {
                    if (b == 'no') return;

                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('GfpGCPPEstResRestful',nome_metodo),
                        params: params,
                        success: function(request) {
                            var obj = Ext.decode(request.responseText);
                            if(obj.success == true){
                                if(nome_metodo.split('_')[0] == 'aplicar'){
                                    params['aplicar_gcpp_ids'] = obj.aplicar_gcpp_ids;
                                    
                                    if(params['aplicar_gcpp_ids'].length == 0){
                                        this.exibirMsgErro("Não há registros válidos para aplicar em folha.");
                                    }else{
                                        new rh.gfp.gcpp.payroll.Window({
                                            action: 'update',
                                            params: params,
                                        }).show();
                                    }
                                }
                                this.getStore().reload();
                            }
                            else{ this.exibirMsgErro(obj.message); }
                        },
                        scope: this
                    });
                }
            })
        }
    },

    acoesItem: function(texto, icone, nome_metodo, tipo_calculo){
        return {
            text: texto,
            iconCls: 'icon-16px '+icone,
            scope: this,
            handler: function(){ this.calcConfDeclAplicGcpp(nome_metodo,tipo_calculo) },
        }
    },

    menuAcoes: function(){
        this._menuAcoes = [
            this.acoesItem('Calcular Selecionados', 'icon-core icon-core-run', 'calcular_gcpp','selecionados'),
            this.acoesItem('Calcular Todos', 'icon-core icon-core-run', 'calcular_gcpp','todos'),
            this.acoesItem('Confirmar Selecionados', 'icon-fopag icon-notebook-plus', 'confirmar_gcpp','selecionados'),
            this.acoesItem('Confirmar Todos', 'icon-fopag icon-notebook-plus', 'confirmar_gcpp','todos'),
            this.acoesItem('Declinar Selecionados', 'icon-fopag icon-notebook-minus', 'declinar_gcpp','selecionados'),
            this.acoesItem('Declinar Todos', 'icon-fopag icon-notebook-minus', 'declinar_gcpp','todos'),
            this.acoesItem('Aplicar Selecionados', 'icon-fopag icon-medal-arrow', 'aplicar_pgto_gcpp','selecionados'),
            this.acoesItem('Aplicar Todos', 'icon-fopag icon-medal-arrow', 'aplicar_pgto_gcpp','todos'),
        ];

        return this._menuAcoes
    },

    itemConfigCustomAction: function(icone, texto, nome_metodo){
        return {
            iconCls: 'icon-16px '+icone,
            tooltip: texto,
            scope: this,
            handler: function(action, index){
                this.calcConfDeclAplicGcpp(nome_metodo,'unico', action._store.getAt(index).data.pk)
            },
        }
    },

    getConfigCustomActions: function(){
        return [
            this.itemConfigCustomAction('icon-core icon-core-run', 'Calcular', 'calcular_gcpp'),
            this.itemConfigCustomAction('icon-fopag icon-notebook-plus', 'Confirmar', 'confirmar_gcpp'),
            this.itemConfigCustomAction('icon-fopag icon-notebook-minus', 'Declinar', 'declinar_gcpp'),
            this.itemConfigCustomAction('icon-fopag icon-medal-arrow', 'Aplicar Pgto', 'aplicar_pgto_gcpp'),
        ];
    },

    comboAno: function(){
        const timeElapsed = Date.now();
        var hoje = new Date(timeElapsed);

        return {
            xtype: 'combo',
            store: new Ext.data.JsonStore({
                proxy: new Ext.data.HttpProxy({
                    url: toolkit.util.Normalize.controller_action('GFPControlador', 'anos_folha'),
                    disableCaching: true,
                    method: 'GET'
                }),
                root: 'root',
                fields: ['pk', 'description']
            }),
            displayField: 'description',
            valueFeild: 'pk',
            emptyText: 'Ano para filtro',
            width: 140,
            triggerAction: 'all',
            value: hoje.getFullYear(),
            listeners: {
                scope: this,
                select: function (combo, record) {
                    var ano = record.json.pk;
                    if(ano == 0){
                        this.removeFilterProperty('periodo_ano', 1, true);
                    }else{
                        this.removeFilterProperty('periodo_ano', 1, false);
                        this.setFilterProperty('periodo_ano', ano, 1, true);
                    }
                }
            }
        }
    },

    comboMes: function(){
        const timeElapsed = Date.now();
        var hoje = new Date(timeElapsed);

        return {
            xtype: 'combo',
            store: [
                [0, 'TODOS'],
                [1, 'JANEIRO'],
                [2, 'FEVEREIRO'],
                [3, 'MARÇO'],
                [4, 'ABRIL'],
                [5, 'MAIO'],
                [6, 'JUNHO'],
                [7, 'JULHO'],
                [8, 'AGOSTO'],
                [9, 'SETEMBRO'],
                [10, 'OUTUBRO'],
                [11, 'NOVEMBRO'],
                [12, 'DEZEMBRO'],
            ],
            emptyText: 'Mês para filtro',
            width: 140,
            triggerAction: 'all',
            value: hoje.getMonth() + 1,
            listeners: {
                scope: this,
                select: function (combo, record) {
                    var mes = record.json[0]
                    if(mes == 0){
                        this.removeFilterProperty('periodo_mes', 2, true);
                    }else{
                        this.removeFilterProperty('periodo_mes', 2, false);
                        this.setFilterProperty('periodo_mes', mes, 2, true);
                    }
                }
            },
        }
    },

    comboTipo: function() {
        return {
            xtype: 'combo',
            store: [
                [0, 'TODOS'],
                [1, 'ESTAGIÁRIO'],
                [2, 'RESIDENTE'],
            ],
            emptyText: 'Selecione o Tipo',
            width: 150,
            triggerAction: 'all',
            value: 0,
            listeners: {
                scope: this,
                select: function(combo, record) {
                    var tipo = record.json[0];

                    if (tipo == 0) {
                        filtro_tipo=['EST', 'RES'];
                    }

                    else if (tipo == 1) {
                        filtro_tipo=['EST'];
                    }

                    else if (tipo == 2) {
                        filtro_tipo=['RES'];
                    }

                    this.removeFilterProperty('servidor__type_by_possession', 3, false);
                    this.setFilterProperty('servidor__type_by_possession__in', filtro_tipo, 3, true);
                }
            },
        }
    },

    constructor: function(cfg) {
        rh.gfp.gcpp_est_res.Grid.superclass.constructor.call(this, cfg);

        const timeElapsed = Date.now();
        var _hoje = new Date(timeElapsed);
        var _ano = _hoje.getFullYear();
        var _mes = _hoje.getMonth() + 1;

        this.setFilterProperty('periodo_ano', _ano, 1, false);
        this.setFilterProperty('periodo_mes', _mes, 2, true);
        this.setFilterProperty('servidor__type_by_possession__in', ['EST', 'RES'], 3, true);
    },

});

core.RestfulGrid.register(
    'rh.gfp.gcpp_est_res.Restful',
    'rh.gfp.gcpp_est_res.Grid'
);