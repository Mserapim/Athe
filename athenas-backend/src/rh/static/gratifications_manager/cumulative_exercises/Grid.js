 Ext._define('rh.gratifications_manager.cumulative_exercises.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gratifications_manager.cumulative_exercises.Restful',

    restWindow: 'rh.gratifications_manager.cumulative_exercises.Window',

    constructor: function(cfg) {
        rh.gratifications_manager.cumulative_exercises.Grid.superclass.constructor.call(this, cfg);

        this.classif_lotacao = cfg.classif_lotacao;

        this.setFilterProperty('designation_substitute__isnull', false, 1001, false);
        this.setFilterProperty('designation_substitute__ativo', true,1002, false);
        this.setFilterProperty('designation_substitute__designacao', true, 1002, false);
        this.setFilterProperty('designation_substitute__lotacao__isnull', false, 1004, false);
        this.setFilterProperty('designation_substituted__lotacao__classificacao__in', [1,2], 1005, true);
    },

    atualizaPagina: function(){
        var store = this.getStore();
        store.baseParams.filter = Ext.encode([]);
        store.baseParams.keyword = null;
        store.load({})
    },

    hideActions: ['add','remove', 'copy', 'edit'],

    configOrderToolBar: ['edit','-','able_to_pay_selected','-','indeferir_selecionados','-','consolidate_able_to_pay','-','search','->','download'],

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = Ext._create('Ext.Toolbar', {
                style: cfg.toolbarStyle,
                items: this.getConfigItemsToolbar(cfg),
            });

            this._dateStartField = new Ext.form.DateField({
                emptyText: 'Início',
                format: 'd/m/Y',
                width: 90,
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    keypress: function (text, event) {
                        if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                            this.setFilterDateRange();
                        }
                    }
                }
            });
            this._dateEndField = new Ext.form.DateField({
                emptyText: 'Fim',
                format: 'd/m/Y',
                width: 90,
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    keypress: function (text, event) {
                        if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                            this.setFilterDateRange();
                        }
                    }
                }
            });

            this._toolbar.add([
                '-',
                this._dateStartField
            ]);
            this._toolbar.add([
                '-',
                this._dateEndField
            ]);

            var filterMenu = this.getFilterMenu();
            if(filterMenu && !(cfg || this).hiddenFilter)
                this._toolbar.add([
                    '-',
                    {
                        text: 'Filtro',
                        iconCls: 'icon-patrimonio icon-pat-filter',
                        menu: filterMenu
                    }
                ]);

            var lotacaoFilterMenu = this.getLotacaoFilterMenu(cfg.classif_lotacao);
            if(lotacaoFilterMenu && !(cfg || this).hiddenFilter)
                this._toolbar.add([
                    '-',
                    {
                        text: 'Filtro Lotação',
                        iconCls: 'icon-patrimonio icon-pat-filter',
                        menu: lotacaoFilterMenu
                    }
                ]);
            

            this._toolbar.add([
                '-',
                {
                    xtype: 'button',
                    text: 'Limpar todos os filtros',
                    iconCls: 'icon-fopag icon-arrow-repeat',
                    handler: function(){ this.setFilterEmpty() },
                    scope: this
                }
            ]);

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

        if(this._dateStartField.getValue() != ''){
            this._dateStartField.setValue('');
        }

        if(this._dateEndField.getValue() != ''){
            this._dateEndField.setValue('');
        }

        this.removeFilterProperty('paid_out', 2, false);
        this.removeFilterProperty('able_to_pay', 3, false);
        this.removeFilterProperty('pay_year', 4, false);
        this.removeFilterProperty('pay_month', 5, false);
        this.removeFilterProperty('consolidated', 6, false);
        this.removeFilterProperty('designation_substitute__isnull', 1001, false);
        this.removeFilterProperty('designation_substitute__ativo', 1002, false);
        this.removeFilterProperty('designation_substitute__designacao', 1002, false);
        this.removeFilterProperty('designation_substitute__lotacao__isnull', 1004, false);
        this.removeFilterProperty('designation_substituted__lotacao__classificacao__in', 1005, false);

        this._toolbar.items.items.forEach(function(item, i){
            if(item.text == 'Filtro'){
                item.menu.items.items.forEach(function(item){
                    item.id == 'todos' ? item.setChecked(true) : item.setChecked(false);
                });
            }
            if(item.text == 'Filtro Lotação'){
                item.menu.items.items.forEach(function(item){
                    item.id == 'todos_lotacao' ? item.setChecked(true) : item.setChecked(false);
                });
            }
        });

        this.atualizaPagina();
    },

    setFilterDateRange: function(){
        var dateStart = Ext.util.Format.date(this._dateStartField.getValue(), 'Y-m-d');
        var dateEnd = Ext.util.Format.date(this._dateEndField.getValue(), 'Y-m-d');

        this.removeFilterProperty('data_inicio__gte', 0, false);
        this.removeFilterProperty('data_fim__lte', 1, false);

        if(dateStart != '' && dateEnd == ''){
            this.addFilterProperty('data_inicio__gte', dateStart, 0, true);
        }else if(dateStart == '' && dateEnd != ''){
            this.addFilterProperty('data_fim__lte', dateEnd, 1, true);
        }else if(dateStart != '' && dateEnd != ''){
            this.addFilterProperty('data_inicio__gte', dateStart, 0, false);
            this.addFilterProperty('data_fim__lte', dateEnd, 1, true);
        }
    },

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: '', dataIndex: 'icons', width: 40, renderer: toolkit.util.formatStatus},
                    {header: 'Substituto', dataIndex: 'servidor_unicode', id: 'autoExpandColumn'},
                    {header: 'Titularidade', dataIndex: 'titularidade', width: 200},
                    {header: 'Substituído', dataIndex: 'servidor_substituido_unicode', width: 200},
                    {header: 'Cumulativa', dataIndex: 'cumulativa', width: 200},
                    {header: 'Data Início', dataIndex: 'data_inicio', width: 100},
                    {header: 'Data Fim', dataIndex: 'data_fim', width: 100},
                    {header: 'Data Início Pgto', dataIndex: 'data_pgto_inicio', width: 100},
                    {header: 'Data Fim Pgto', dataIndex: 'data_pgto_fim', width: 100},
                    {header: 'Qtd Dias', dataIndex: 'qtd_dias', width: 70},
                    {header: 'Período Pgto', dataIndex: 'periodo_pgto', width: 80},
                    {header: 'Parcelas de Pgto', dataIndex: 'payment_installments', width: 100},
                    {header: 'Período de Venda (Janela)', dataIndex: 'periodo', hidden: true, width: 100},
                    {header: 'Gedoc', dataIndex: 'gedoc', width: 100},
                ]
            );
        
        return this._columnModel;
    },

    setParamsFilterMenu: function(chk, option){
        this.removeFilterProperty('paid_out', 2, false);
        this.removeFilterProperty('able_to_pay', 3, false);
        this.removeFilterProperty('pay_year', 4, false);
        this.removeFilterProperty('consolidated', 6, false);
        this.removeFilterProperty('indeferido', 7, false);

        var autoLoadPayMonth = (option == 'todos' || !chk.checked == false) ? true : false;
        this.removeFilterProperty('pay_month', 5, autoLoadPayMonth);

        this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
            if(item.id != option){ item.setChecked(false); }

            if(!chk.checked == false && item.id == 'todos'){ item.setChecked(true); }
        });

        if(option == 'pagos' && !chk.checked == true){
            this.addFilterProperty('paid_out', true, 2, true);
        }else if(option == 'aptos' && !chk.checked == true){
            this.addFilterProperty('paid_out', false, 2, false);
            //this.addFilterProperty('able_to_pay', true, 3, true);
            this.addFilterProperty('consolidated', false, 6, false);
            this.addFilterProperty('indeferido', false, 7, true);
        }else if(option == 'consolidados' && !chk.checked == true){
            this.addFilterProperty('paid_out', false, 2, false);
            this.addFilterProperty('indeferido', false, 7, false);
            this.addFilterProperty('consolidated', true, 6, true);
        }else if(option == 'indeferidos' && !chk.checked == true){
            this.addFilterProperty('paid_out', false, 2, false);
            this.addFilterProperty('able_to_pay', false, 3, false);
            this.addFilterProperty('consolidated', false, 6, false);
            this.addFilterProperty('indeferido', true, 7, true);
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
                id: 'aptos',
                text: 'Somente Aptos a pgto',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'aptos') },
            },
            // {
            //     id: 'pendentes',
            //     text: 'Somente Pendentes',
            //     checked: false,
            //     scope: this,
            //     hideOnClick: false,
            //     handler: function(chk) { this.setParamsFilterMenu(chk, 'pendentes') },
            // },
            {
                id: 'pagos',
                text: 'Somente Pagos',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'pagos') },
            },
            {
                id: 'consolidados',
                text: 'Somente Consolidados',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'consolidados') },
            },
            {
                id: 'indeferidos',
                text: 'Somente Indeferidos',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'indeferidos') },
            },
        ];

        return this._getFilterMenu
    },
    
    setParamsLotacaoFilterMenu: function(chk, opcaoId){
        if(opcaoId == 'Todos' && !chk.checked == true){
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.text != 'Todos'){ item.setChecked(false); }
            });

            this.removeFilterProperty('designation_substituted__lotacao__classificacao__in', 1005, true);
        }else if(opcaoId == 'Todos' && !chk.checked == false){
            var item =  this._toolbar.activeMenuBtn.menu.items.items[1];
            item.setChecked(true);
            
            this.setFilterProperty('designation_substituted__lotacao__classificacao__in', [item.id], 1005, true);
        }else{
            var itensFiltrar = !chk.checked == true ? [opcaoId] : [];
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.text == 'Todos'){
                    item.setChecked(false);
                }else if(item.text != 'Todos' && item.id != opcaoId && item.checked == true){
                    itensFiltrar.push(item.id);
                }
            });

            if(itensFiltrar.length > 0){
                this.setFilterProperty('designation_substituted__lotacao__classificacao__in', itensFiltrar, 1005, true);
            }else{
                this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                    if(item.text == 'Todos'){
                        item.setChecked(true);
                    }else if(item.id != opcaoId){
                        item.setChecked(false);
                    }
                });
                
                this.removeFilterProperty('designation_substituted__lotacao__classificacao__in', 1005, true);
            }
        }
    },


    getLotacaoFilterMenu: function(classif_lotacao){
        var _getLotacaoFilterMenu = [{
            id: 0,
            text: 'Todos',
            checked: false,
            scope: this,
            hideOnClick: false,
            handler: function(chk) { this.setParamsLotacaoFilterMenu(chk, 'Todos') },
        }];
        var that = this;
        classif_lotacao.forEach(function(item){
            _getLotacaoFilterMenu.push({
                id: item.id,
                text: item.titulo,
                checked: [1,2].includes(item.id) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { that.setParamsLotacaoFilterMenu(chk, item.id) },
            });
        });

        return _getLotacaoFilterMenu;
    },

    _ableToPaySelected: function(){
        var selecteds = this.getSelectionModel().getSelections().map(function(a){ return a.id; });

        if(selecteds.length == 0){
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Escolha pelo menos um registro para autorizar o pagamento.'
            });
        }else{
            Ext.Msg.show({
                msg: 'Tem certeza que deseja autorizar pagamentos para os registros selecionados?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (b) {
                    if (b == 'no') return;
    
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('GMCumulativeExercises','able_to_pay_selected'),
                        params: { ids: selecteds },
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
                }
            });
        }
    },

    _indeferirSelecionados: function(){
        var selecteds = this.getSelectionModel().getSelections().map(function(a){ return a.id; });

        if(selecteds.length == 0){
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Escolha pelo menos um registro para indeferir!.'
            });
        }else{
            Ext.Msg.show({
                msg: 'Tem certeza que deseja Indeferir os registros selecionados?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (b) {
                    if (b == 'no') return;
    
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('GMCumulativeExercises','indeferir_selecionados'),
                        params: { ids: selecteds },
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
                }
            });
        }
    },
















    _consolidateAbleToPay: function(){
        Ext.Msg.show({
            msg: 'Tem certeza que deseja consolidar os registros aptos a pagamento?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                var dt_start = this._dateStartField.getValue();
                var dt_end = this._dateEndField.getValue();
                var search_field = ''

                this._configItemsToolbar.forEach(function(item, i){
                    if(item.emptyText == 'Motor de buscas'){
                        search_field = item.getValue();
                    }
                });

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GMCumulativeExercises','consolidate_able_to_pay'),
                    params: {
                        search_field: search_field,
                        dt_start: dt_start,
                        dt_end: dt_end,
                    },
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
            }
        });
    },

    getConfigActionsItems: function(cfg){
        if(!this._configActionsItems){
            rh.gfp.paycheckdifference.difference_payroll.Grid.superclass.getConfigActionsItems.call(this, cfg);
            var _menu = {
                able_to_pay_selected:{
                    text: 'Autorizar Pgto para Selecionados',
                    iconCls: 'icon-fopag icon-money-plus',
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    },
                    tooltip: 'Autorizar Pgto para Selecionados',
                    disabled: false,
                    scope: this,
                    handler: function(){ this._ableToPaySelected(); },
                },
                indeferir_selecionados:{
                    text: 'Indefeir Selecionados',
                    iconCls: 'icon-socialsecurity icon-socialsecurity-negative',
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    },
                    tooltip: 'Indeferir Selecionados',
                    disabled: false,
                    scope: this,
                    handler: function(){ this._indeferirSelecionados(); },
                },
                consolidate_able_to_pay:{
                    text: 'Consolidar Aptos',
                    iconCls: 'icon-fopag icon-table-plus',
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    },
                    tooltip: 'Consolidar Aptos',
                    disabled: false,
                    scope: this,
                    handler: function(){ this._consolidateAbleToPay(); },
                },
            };
            Ext.apply(this._configActionsItems, _menu);

        }
        return this._configActionsItems;
    },
});

core.RestfulGrid.register(
    'rh.gratifications_manager.cumulative_exercises.Restful',
    'rh.gratifications_manager.cumulative_exercises.Grid'
);
