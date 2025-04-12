Ext._define('rh.gfp.vacation.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.vacation.Window',

    hideActions: ["remove", "copy", "edit"],

    hideItemsToolbar: ["add", "edit", "remove"],

    API_CLASS: 'GFPPaymentVacation',

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
                    { 
                        header: 'Status do RH',
                        dataIndex: 'status_conference_payment',
                        width: 70,
                        hidden: true
                    },
                    { 
                        header: 'Status',
                        dataIndex: 'payroll_ctrl_status_display',
                        width: 80,
                        renderer: function(value, meta, record, rowIndex, colIndex, store) {
                            if(value == 'Aprovado'){
                                meta.style = 'font-weight:bold; width: 80px; text-overflow: ellipsis; padding: 3px 3px 3px 5px; color:green'
                            } else if(value == 'Negado'){
                                meta.style = 'font-weight:bold; width: 80px; text-overflow: ellipsis; padding: 3px 3px 3px 5px; color:red'
                            }else if(value == 'Finalizado'){
                                meta.style = 'font-weight:bold; width: 80px; text-overflow: ellipsis; padding: 3px 3px 3px 5px;'
                            }else {
                                meta.style = 'font-weight:bold; width: 80px; text-overflow: ellipsis; padding: 3px 3px 3px 5px; color:gray'
                            }
                            return value; 
                        }
                    },
                    { header: 'Matrícula' ,dataIndex: 'employee_registry',  width: 60, hidden: true},
                    { header: 'Servidor', dataIndex: 'employee_unicode', id: 'autoExpandColumn' },
                    { header: 'Situação', dataIndex: 'status_display',  width: 80, hidden: true},
                    { header: 'Tipo Servidor' ,dataIndex: 'employee_type', width: 80 },
                    { header: 'Atividade', dataIndex: 'activity_unicode', width: 200},
                    { header: 'Status da Atividade', dataIndex: 'activity_label', width: 70, hidden: true},
                    { header: 'Grupo', dataIndex: 'group_period', width: 150 },
                    { header: 'Início Aquisição', dataIndex: 'start_date_acquisition', width: 70, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Final Aquisição', dataIndex: 'end_date_acquisition', width: 70, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Início de Fruição', dataIndex: 'start_date_fruition', width: 70, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Início das Férias', dataIndex: 'start_date', width: 70, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Fim das Férias', dataIndex: 'end_date', width: 70, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Dias programados', dataIndex: 'days', width: 40 },
                    { header: 'Valor Calculado', dataIndex:'calculated_value', width: 80, renderer: toolkit.util.formatCurrency},
                    { header: 'Valor Confirmado', dataIndex:'confirmed_value', width: 80, renderer: toolkit.util.formatCurrency},
                    { header: 'Valor Pago', dataIndex:'paid_value', width: 80, renderer: toolkit.util.formatCurrency},
                    { header: 'Comp. Pagamento', dataIndex:'competence_paid', width: 100},
                    { header: 'Marcação da escala', dataIndex: 'from_scale_display', width: 90, renderer: function (value) { return (value ? 'SIM' : 'NÃO'); }, hidden: true },
                    { header: 'Criado por', dataIndex: 'created_by_unicode', width: 100,hidden: true },
                    { header: 'Criado em', dataIndex: 'created_at', width: 90,hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                    { header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 100,hidden: true },
                    { header: 'Modificado em', dataIndex: 'modified_at', width: 90,hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                    { header: 'Autorizado por', dataIndex: 'authorized_by_unicode', width: 100,hidden: true },
                    { header: 'Autorizado em', dataIndex: 'authorized_at', width: 90, hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                ]
            );

        return this._columnModel;
    },

    doDownload: function() {
        this.removeFilterProperty('status', 10, false);
        this.removeFilterProperty('status__isnull', 12, false);
        var config = {
            filter: Ext.encode(this.getFilter()),
            keyword: this.getKeywordField().getValue(),
            start: 0,
            limit: this.getStore().getTotalCount(),
            format: 'text/csv'
        };
        var rest = this.factoryRestful();
        var url = rest.getRoute('export').url + '?' + Ext.urlEncode(config);

        window.open(url, '_self');
    },

    getConfigItemsToolbar: function(cfg) {
        var search = [
            'Buscar por: ',
            this.getKeywordField(cfg),
            '-'
        ]
        var menu = [];
        var menuFiltroStatus = this.menuFiltroStatus();

        menu.push(
            this.getAuthorizeAction(),
            '-',
            this.getPaymentAction(),
            '-',
            search,
            "->",
            {
                text: 'Filtrar Status',
                iconCls: 'icon-patrimonio icon-pat-filter',
                menu: menuFiltroStatus,
            },
            '-',
            '-',
            {
                text: 'Download',
                iconCls: 'icon-core icon-core-csv',
                scope: this,
                handler: this.doDownload
            }
        )

        return menu;
    },

    getConfigCustomActions: function () {
        return [
            {
                tooltip: "Apto para pagamento",
                scope: this,
                iconCls: true,
                icon: "/" + global.Context + "/static/rh/images/core/publication-confirmed.png",
                handler: function (action, index) {
                    if (!this.getSelectionModel().isSelected(index)) this.getSelectionModel().selectRow(index);
                        this.authorize(true);
                },
            },
            '-',
            {

                tooltip: 'Inapto para pagamento',
                scope: this,
                iconCls: true,
                icon: "/" + global.Context + "/static/rh/images/core/publication-canceled.png",
                handler: function (action, index) {
                    if (!this.getSelectionModel().isSelected(index)) this.getSelectionModel().selectRow(index);
                        this.authorize(false);
                },

            },
            '-',
            {
                tooltip: 'Calcular valor a pagar',
                scope: this,
                iconCls: true,
                icon: "/" + global.Context + "/static/rh/images/fopag/images/table-plus.png",
                handler: function (action, index) {
                    if (!this.getSelectionModel().isSelected(index)) this.getSelectionModel().selectRow(index);
                        this.calculate();
                },
            },
        ];
    },

    getAuthorizeAction: function () {
        return [
            {
                text: "Apto para pagamento",
                tooltip: 'Conferir o pagamento para selecionados',
                disabled: false,            
                scope: this,
                iconCls: true,
                icon: "/" + global.Context + "/static/rh/images/core/publication-confirmed.png",
                handler: function () {
                    this.authorize(true);
                },
            },
            {
                text: "Inapto para pagamento",
                tooltip: 'Conferir o pagamento para selecionados',
                scope: this,
                iconCls: true,
                icon: "/" + global.Context + "/static/rh/images/core/publication-canceled.png",
                handler: function () {
                    this.authorize(false);
                },
            }
        ]
    },

    getPaymentAction: function () {
        return [
            {
                text: "Calcular",
                tooltip: 'Calcular valor a pagar',
                disabled: false,            
                scope: this,
                iconCls: 'icon-fopag icon-table-plus',
                handler: function () {
                    this.calculate(true);
                },
            },
            '-',
            {
                text: "Implantar",
                tooltip: 'Implantar as verbas conferidas em folha',
                scope: this,               
                iconCls: 'icon-fopag icon-money-plus',
                handler: function () {
                    this.implement(true);
                },
            }, 
            '-'
        ]
    },

    authorize: function (authorize) {
        var selected = [this.getSelectionModel().getSelections().map(function(a){ return a.id; })]
        if (authorize) {
            msg = 'Deseja autorizar o pagamento para o/os itens selecionados ?'
            method = 'control_checked'
        }else{
            msg = 'Deseja negar pagamento para o/os itens selecionados ?'
            method = 'control_declined'
        }
        if (!selected) {
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: "Selecione um item",
            });
        } else {
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: msg,
                scope: this,

                fn: function (b) {
                    if (b == 'no') return;
                    this.executeAction(method, selected)
                },
            });
        }

    },

    calculate: function(get_all=null){
        method = 'control_calculate'
        msg = 'Deseja fazer o cálculo dos abonos e férias ?'
        if (get_all){
            selected = null
        } else {
            var selected = this.getSelectionModel().getSelected().id; 
        }

        Ext.Msg.show({
            title: this.title,
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            msg: msg,
            scope: this,

            fn: function (b) {
                if (b == 'no') return;
                this.executeAction(method, selected)
            },
        });

    },

    implement: function(get_all=null){
        method = 'control_implement'
        if (get_all){
            var selected = [this.getSelectionModel().getSelections().map(function(a){ return a.id; })]
            msg = 'Deseja implantar a gratificação/abono selecionada para pagamento em folha ?'
        } else {
            var selected = this.getSelectionModel().getSelected().id; 
            msg = 'Deseja implantar a gratificação/abono selecionada para pagamento em folha ?'
        }
        new toolkit.gfp.VacationForm({
            method: method,
            selected: selected,
            month: this._month,
            year: this._year
        }).show()
    },

    executeAction: function(method, selecteds=null){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(this.API_CLASS, method),
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
    },

    observeFilters: function () {
        this.setFilterProperty('usufruct__payment_year', this._year, 0, false);
        if(this._month){
            this.setFilterProperty('usufruct__payment_month', this._month, 1, false);
        }else{
            this.removeFilterProperty('usufruct__payment_month', 1, false);
        }

        if (this._employeeType){
            this.removeFilterProperty('usufruct__activity__acquisition_period__employee__tipo__in', 4, false);
            this.setFilterProperty('usufruct__activity__acquisition_period__employee__tipo__in', this._employeeType, 4, false);
        }
        if(this._usufructType){
            if (this._usufructType == 2) {
                this.removeFilterProperty('usufruct__status', -5, false);
                this.setFilterProperty('usufruct__status', 4096, 5, false);
            }
            else if (this._usufructType == 1) {
                this.removeFilterProperty('usufruct__status', 5, false);
                this.setFilterProperty('usufruct__status', 4096, -5, false);
            }
            else{
                this.removeFilterProperty('usufruct__status', 5, false);
                this.removeFilterProperty('usufruct__status', -5, false);
            }
            
        }
        this.getStore().reload();
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
                        filtros_aplicar.push(item.value);
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
                    filtros_aplicar.push(item.value);
                }
            });
        }

        if(filtros_aplicar.length > 0){
            this.setFilterProperty('payroll_ctrl_status__in', filtros_aplicar, 4, true);
        }else{
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.id == 'todos' && !chk.checked == false){
                    item.setChecked(true);
                }
            });
            this.removeFilterProperty('payroll_ctrl_status__in', 4, true);
        }
    },

    menuFiltroStatus: function() {
        this._menuFiltroStatus = [
            {
                id: 'todos',
                text: 'Todos',
                checked: true,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'todos') },
            },
            {
                id: 'analise',
                value: 1,
                text: 'Em análise',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'analise') },
            },
            {
                id: 'negado',
                value: 2,
                text: 'Negado',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'negado') },
            },
            {
                id: 'aprovado',
                value: 3,
                text: 'Aprovado',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'aprovado') },
            },
            {
                id: 'finalizado',
                value: 4,
                text: 'Finalizado',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'finalizado') },
            }
        ];
        return this._menuFiltroStatus;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        // Parâmetros iniciais da tela
        const timeElapsed = Date.now();
        this._today = new Date(timeElapsed);
        this._year = this._today.getFullYear();
        this._month = this._today.getMonth() +1;
        this._usufructType = undefined
        this.keywordFieldWidth = 140
        
        Ext.apply(cfg, { gridAutoLoad: false });
        Ext.applyIf(cfg, {
            columnAction: true, 
        });
        rh.gfp.vacation.Grid.superclass.constructor.call(this, cfg);

        this._toolbar.insert(
            10,
            {
                xtype: 'combo',
                store: [
                    [1, 'GRATIFICAÇÃO'],
                    [2, 'ABONO'],
                    [3, 'GRATIFICAÇÃO E ABONO'],
                ],
                emptyText: 'Gratificação ou Abono',
                width: 140,
                triggerAction: 'all',
                listeners: {
                    scope: this,
                    select: function (combo, record) {
                        var store = this.getStore();

                        if (record.get('field1') != 0)
                            this._usufructType = record.get('field1');
                            
                        else
                            this._usufructType = null
                            
                        this.observeFilters()
                    }
                }
            },
            '-',
            {
                xtype: "combo",
                displayField: "Tipo",
                emptyText: 'Tipo',
                width: 140,
                triggerAction: 'all',
                store: [
                    ['M', 'MEMBRO'],
                    ['S', 'SERVIDOR'],
                    ['A', 'TODOS']
                ],
                listeners: {
                    scope: this,
                    select: function (combo, record) {
                        var store = this.getStore();
                        if (record.get('field1') != 'A')
                            this._employeeType = [ record.get('field1'), ];
                            
                        else
                            this._employeeType = ['M', 'S']
                            
                        this.observeFilters()
                    }
                }

            },
            '-',
                {
                    xtype: 'combo',
                    store: new Ext.data.JsonStore({
                        proxy: new Ext.data.HttpProxy({
                            url: toolkit.util.Normalize.controller_action('GFPPaymentVacation', 'buscar_lista_anos'),
                            disableCaching: true,
                            method: 'GET'
                        }),
                        root: 'root',
                        fields: ['pk', 'description']
                    }),
                    displayField: 'description',
                    valueFeild: 'pk',
                    emptyText: 'Ano para filtro',
                    width: 90,
                    triggerAction: 'all',
                    value: this._today.getFullYear(),
                    listeners: {
                        scope: this,
                        select: function (combo, record) {
                            var store = this.getStore();

                            if (record.get('pk') != 0)
                                this._year = record.get('pk')
                            else
                                this._year = null
                                
                            this.observeFilters()
                        }
                    }
                },
                '-',
                {
                    xtype: 'combo',
                    store: [
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
                    width: 90,
                    triggerAction: 'all',
                    value: this._month,
                    listeners: {
                        scope: this,
                        select: function (combo, record) {
                            var store = this.getStore();

                            if (record.get('field1') != 0)
                                this._month = record.get('field1');
                                
                            else
                                this._month = null
                                
                            this.observeFilters()
                        }
                    }
                },
                '-',
                    
        );

        this.observeFilters();
    }
});

toolkit.gfp.VacationForm = Ext.extend(
    Ext.Window,
    {
        getFormPanel: function()  {
            if(!this._formPanel)
                this._formPanel = Ext._create('Ext.form.FormPanel', {
                    border: false,
                    frame: true,
                    items: [
                        {
                            xtype: 'rest-autocompletefield',
                            fieldLabel: 'Folha',
                            name: 'payroll',
                            rest: 'rh.gfp.payroll.PayrollRestful',
                            allowBlank: false,
                        },
                    ]
                });
    
            return this._formPanel;
        },

        executeAction: function(method, selecteds=null, month=null, year=null){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action('GFPPaymentVacation', method),
                params: { 
                    ids: selecteds,
                    payroll: this.getFormPanel().getForm().findField('payroll').getValue(),
                    month: month,
                    year:year
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

            this.destroy();
    
        },

        constructor: function (cf) {
            if (!cf) cf = {}

            Ext.apply(
                cf,
                {
                    title: 'Implantar - Abono/Gratificação',
                    closable: true,
                    resizable: false,
                    width: 480,
                    border: false,
                    modal: true,
                    itens: [
                        this.getFormPanel()
                    ],
                    buttons: [
                        {
                            xtype: 'button',
                            iconCls: 'icon-siatu icon-siatu-move-down',
                            text: 'Implantar',
                            width: 100,
                            height: 25,
                            scope: this,
                            handler: function (){
                                this.executeAction(cf.method, cf.selected, cf.month, cf.year)
                            }
                            
                        }, 
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.destroy
                        }
                    ]
                }
            );

            toolkit.gfp.VacationForm.superclass.constructor.call(this, cf);
            this.add(this.getFormPanel());
        }
    }
);

core.RestfulGrid.register(
    'rh.gfp.vacation.Restful',
    'rh.gfp.vacation.Grid'
);
