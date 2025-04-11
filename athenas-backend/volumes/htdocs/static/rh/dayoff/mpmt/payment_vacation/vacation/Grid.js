Ext._define('rh.dayoff.mpmt.payment_vacation.vacation.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.dayoff.mpmt.payment_vacation.vacation.Restful',

    hideActions: ["remove", "copy", "edit"],

    hideItemsToolbar: ["add", "edit", "remove"],

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
                    {
                        id: 'icons',
                        dataIndex: 'icons',
                        header: '',
                        width: 120,
                        sortable: false,
                        renderer: toolkit.util.formatStatus,
                        menuDisabled: true
                    },
                    { 
                        header: 'Status',
                        dataIndex: 'status_conference_payment',
                        width: 100,
                        renderer: function(value, meta, record, rowIndex, colIndex, store) {
                            meta.style = 'font-weight:bold; width: 100px; text-overflow: ellipsis; padding: 3px 3px 3px 5px;'
                            return value; 
                        }
                    },
                    { header: 'Matrícula' ,dataIndex: 'employee_registry',  width: 60, hidden: true},
                    { header: 'Servidor', dataIndex: 'employee_unicode', id: 'autoExpandColumn' },
                    { header: 'Situação', dataIndex: 'status_display',  width: 80 },
                    { header: 'Tipo Servidor' ,dataIndex: 'employee_type', width: 80 },
                    { header: 'Atividade', dataIndex: 'activity_unicode', width: 200 },
                    { header: 'Status da Atividade', dataIndex: 'activity_label', width: 90 },
                    { header: 'Grupo', dataIndex: 'group_period', width: 150 },
                    { header: 'Início das Férias', dataIndex: 'start_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Fim das Férias', dataIndex: 'end_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Dias programados', dataIndex: 'days', width: 40 },
                    { header: 'Comp. Pagamento', dataIndex:'competence_paid', width: 100},
                    { header: 'Marcação da escala', dataIndex: 'from_scale_display', width: 90, renderer: function (value) { return (value ? 'SIM' : 'NÃO'); }, hidden: true },
                    { header: 'Criado por', dataIndex: 'created_by_unicode', width: 100,hidden: true },
                    { header: 'Criado em', dataIndex: 'created_at', width: 90,hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                    { header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 100,hidden: true },
                    { header: 'Modificado em', dataIndex: 'modified_at', width: 90,hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                    { header: 'Autorizado por', dataIndex: 'checked_by_unicode', width: 100,hidden: true },
                    { header: 'Autorizado em', dataIndex: 'checked_at', width: 90, hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                ]
            );

        return this._columnModel;
    },

    doDownload: function() {

        this.removeFilterProperty('ctrl_payments__isnull', 5, false);
        this.removeFilterProperty('ctrl_payments__status', 10, false);
        this.removeFilterProperty('ctrl_payments__status__isnull', 12, false);
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

    getFilterMenu: function() {

        return [
            {
                text: 'Status de Conferência',
                menu: [
                    {
                        text: 'Sem análise',
                        scope: this,
                        checked: true,
                        group: 'status',
                        hideOnClick: false,
                        handler: function() { this.toggleCtrlPayment('pendent'); }
                    },
                    {
                        text: 'Declinados',
                        scope: this,
                        checked: false,
                        group: 'status',
                        hideOnClick: false,
                        handler: function() { this.toggleCtrlPayment('declined'); }
                    },
                    {
                        text: 'Conferido',
                        scope: this,
                        checked: false,
                        group: 'status',
                        hideOnClick: false,
                        handler: function() { this.toggleCtrlPayment('checked'); }
                    },
                    {
                        text: 'Todos',
                        scope: this,
                        checked: false,
                        group: 'status',
                        hideOnClick: false,
                        handler: function() { this.toggleCtrlPayment('all'); }
                    }
                ]
            }
        ];
    },

    toggleCtrlPayment: function(value) {
        var obj = this
        switch (value) {
            case 'checked':
                obj.removeFilterProperty('ctrl_payments__isnull', 5, false);
                obj.removeFilterProperty('ctrl_payments__status', 10, false);
                obj.removeFilterProperty('ctrl_payments__status__isnull', 12, false);
                

                obj.setFilterProperty('ctrl_payments__isnull', false, 5, false);
                obj.setFilterProperty('ctrl_payments__status',3, 10, false);
                obj.getStore().reload();

                break
            case 'declined':
                obj.removeFilterProperty('ctrl_payments__isnull', 5, false);
                obj.removeFilterProperty('ctrl_payments__status', 10, false);
                obj.removeFilterProperty('ctrl_payments__status__isnull', 12, false);

                obj.setFilterProperty('ctrl_payments__isnull', false, 5, false);
                obj.setFilterProperty('ctrl_payments__status', 2, 10, false);
                obj.getStore().reload();
                break
            case 'all':
                obj.removeFilterProperty('ctrl_payments__isnull', 5, false);
                obj.removeFilterProperty('ctrl_payments__status', 10, false);
                obj.removeFilterProperty('ctrl_payments__status__isnull', 12, false);
                
                obj.getStore().reload();

                break
            case 'default':               
                obj.getStore().reload();
                break
            default:
                obj.removeFilterProperty('ctrl_payments__isnull', 5, false);
                obj.removeFilterProperty('ctrl_payments__status', 10, false);
                obj.removeFilterProperty('ctrl_payments__status__isnull', 12, false);

                obj.setFilterProperty('ctrl_payments__isnull', true, 5, false);
                obj.setFilterProperty('ctrl_payments__status__isnull', true, 12, false);
                obj.getStore().reload();
                break
                
        }
    },

    getConfigItemsToolbar: function(cfg) {
        var search = [
            'Buscar por: ',
            this.getKeywordField(cfg),
            '-'
        ]
        var menu = [];
        menu.push(
            this.getAuthorizeAction(),
            '-',
            search,
            "->",
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
                iconCls: true,
                icon: "/" + global.Context + "/static/rh/images/pasu_autorizado.png",
                tooltip: "Conferir item selecionado",
                scope: this,
                handler: function (action, index) {
                    if (!this.getSelectionModel().isSelected(index)) this.getSelectionModel().selectRow(index);
                        this.authorize(true);
                },
            },
        ];
    },

    getAuthorizeAction: function () {
        return [
            {
                text: "Conferido",
                tooltip: 'Conferir o pagamento para selecionados',
                disabled: false,            
                scope: this,
                iconCls: true,
                icon: "/" + global.Context + "/static/rh/images/pasu_autorizado.png",
                handler: function () {
                    this.authorize(true);
                },
            },
            {
                text: "Declinado",
                tooltip: 'Conferir o pagamento para selecionados',
                scope: this,
                iconCls: true,
                icon: "/" + global.Context + "/static/rh/images/pasu_nao_autorizado.png",
                handler: function () {
                    this.authorize(false);
                },
            }
        ]

    },

    authorize: function (authorize) {
        const selecteds = this.getSelectionModel().getSelections().map(function(a){ return a.id; });

        const filterParams = {"filter":this.getSelectionModel().grid.store.baseParams.filter}

        const keyword = this.getSelectionModel().grid.store.baseParams.keyword
      
        const params = {...filterParams}

        if (selecteds.length > 0)
            params['ids'] = selecteds

        if (keyword)
            params['keyword'] = keyword
    
        if (authorize){
            method = 'control_checked'
            msg = 'Deseja conferir o/os itens selecionados ?'
            if (!selecteds) {
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
                        this.executeAction(method, params)
                    },
                });
            }
        }else{
            method = 'control_declined'
            this.openPaymentWindow(method, 'Pagamento', null)
        }

    },

    executeAction: function(method, params){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('DAYOFFPaymentVacation', method),
            params:params,
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

    observeFilters: function (cfg,valor='default') {
        if (this._month && this._year){
            const date = new Date(this._year, this._month).toISOString().substring(0, 10);
            var d_end = new Date(this._year, this._month+1)

            d_end.setDate(d_end.getDate() - 1);
            d_end = d_end.toISOString().substring(0, 10)

            this.setFilterProperty('payment_year', this._year, 0, false);
            this.setFilterProperty('payment_month', this._month, 1, false);
        }
        if (this._employeeType){
            this.setFilterProperty('activity__acquisition_period__employee__tipo__in', this._employeeType, 4, false);
        }
        this.toggleCtrlPayment(valor)
    },

    openPaymentWindow: function (actionCustom, title, type_window) {
        var selections = this.getSelectionModel().getSelections();
        if (selections.length > 1){
            return Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: "Selecione um usufruto."
            });
        }
        if (selections.length == 1){
            var usufruct = selections.map(function (item) {  return item.get('pk'); });
            var activity = selections.map(function (item) { return item.get('activity'); });

            Ext._create("rh.dayoff.mpmt.payment_vacation.PaymentWindow", {
                // values: values,
                actionCustom: actionCustom,
                title: title,
                usufruct: usufruct,
                activity: activity,
                // acquisitionPeriodRestful: this.resourceRestful,
                type_window: type_window,
                // usufructModifieds: modifieds,
                // externalCallback: _manage.externalCallback,
                selected: selections,
                // select: this.getUsufructsGrid().getSelectionModel().getSelected(),
            }).show();
        }else{
            return Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: "Selecione um usufruto."
            });
        }

    },

    buscarComboAno: function(cfg){
        return {
            xtype: 'combo',
            store: new Ext.data.JsonStore({
                proxy: new Ext.data.HttpProxy({
                    url: toolkit.util.Normalize.controller_action('DAYOFFPaymentVacation', 'buscar_lista_anos'),
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
            value: this._today.getFullYear(),
            listeners: {
                scope: this,
                select: function (combo, record) {
                    var store = this.getStore();

                    if (record.get('pk') != 0)
                        this._year = record.get('pk')
                    else
                        this._year = null
                        
                    this.observeFilters(cfg)
                }
            }
        }
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        // Parâmetros iniciais da tela
        const timeElapsed = Date.now();
        this._today = new Date(timeElapsed);
        this._year = this._today.getFullYear();
        this._month = this._today.getMonth() + 1;
        
        Ext.apply(cfg, { gridAutoLoad: false });
        Ext.applyIf(cfg, {
            columnAction: true, 
        });
        rh.dayoff.mpmt.payment_vacation.vacation.Grid.superclass.constructor.call(this, cfg);

        this._toolbar.insert(
            3,
            {
                xtype: "combo",
                displayField: "Tipo",
                emptyText: 'Tipo',
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
                            
                        this.observeFilters(cfg)
                    }
                }

            },
            '-',
                this.buscarComboAno(cfg),
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
                    width: 140,
                    triggerAction: 'all',
                    value: this._today.getMonth() + 1,
                    listeners: {
                        scope: this,
                        select: function (combo, record) {
                            var store = this.getStore();

                            if (record.get('field1') != 0)
                                this._month = record.get('field1');
                            else
                                this._month = null
                                
                            this.observeFilters(cfg)
                        }
                    }
                },
                '-',
                    
        );

        this.observeFilters(cfg, valor='');
        //this.toggleCtrlPayment();
    },

});

core.RestfulGrid.register(
    'rh.dayoff.mpmt.payment_vacation.vacation.Restful',
    'rh.dayoff.mpmt.payment_vacation.vacation.Grid'
);
