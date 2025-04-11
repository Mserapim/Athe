Ext._define('corregedoria.cirdir.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'corregedoria.cirdir.Restful',
    restWindow: 'corregedoria.cirdir.Window',

    configOrderToolBar: ['search', 'menu', 'applyFilter', 'reports', 'menuHealthArea', 'applyFilterHealthArea', 'reportsHealthArea', ],


    getReportsHealthAreaAction: function(cfg) {
        if(!this._reportsHealthAreaAction){
            this._reportsHealthAreaAction = new Ext.Button({
                xtype: 'button',
                text: 'Relatórios',
                iconCls: 'icon-crgmpe icon-crgmpe-application-pdf',
                disabled: true,
                hidden: true,
                menu: [

                ]
            });
        }
        return this._reportsHealthAreaAction;
    },

    filterMemberHealthArea: function()  {
        this.showAllHealthArea(false);
        this.addFilterProperty('employee__tipo', 'M', 2010, true);
    },

    filterEmployeeHealthArea: function()  {
        this.showAllHealthArea(false);
        this.addFilterProperty('employee__tipo', 'S', 2020, true);
    },

    showAllHealthArea: function(exec)  {
        this.removeFilterProperty('employee__tipo', 2010, false);
        this.removeFilterProperty('employee__tipo', 2020, exec);
    },

    getFilled: function() {
        this.getShowAllHealthArea(false);
        this.addFilterProperty('authorization_health', true, 1010, false);
        this.addFilterProperty('healths__isnull', false, 1011, true);
    },

    getNoFilled: function() {
        this.getShowAllHealthArea(false);
        this.addFilterProperty('healths__isnull', true, 1020, true);
    },

    getShowAllHealthArea: function(exec) {
        this.removeFilterProperty('authorization_health', 1010, false);
        this.removeFilterProperty('healths__isnull', 1011, false);
        this.removeFilterProperty('healths__isnull', 1020, exec);
    },

    getApplyFilterHealthAreaAction: function() {
        if(!this._applyFilterHealthAreaAction){
            this._applyFilterHealthAreaAction = new Ext.Button({
                xtype: 'button',
                text: 'Exibir',
                iconCls: 'icon-crgmpe icon-crgmpe-find',
                hidden: true,
                menu: [
                    {
                        text: 'Integrantes',
                        iconCls: 'icon-crgmpe icon-crgmpe-stabilization',
                        scope: this,
                        menu: [
                            {
                                text: 'Somente Membros',
                                iconCls: 'icon-crgmpe icon-crgmpe-man-black',
                                scope: this,
                                handler: function() { this.filterMemberHealthArea(); }
                            },
                            {
                                text: 'Somente Servidores',
                                iconCls: 'icon-crgmpe icon-crgmpe-man-blue',
                                scope: this,
                                handler: function() { this.filterEmployeeHealthArea(); }
                            },
                            '-',
                            {
                                text: 'Membros/Servidores',
                                iconCls: 'icon-crgmpe icon-crgmpe-user-group',
                                scope: this,
                                handler: function() { this.showAllHealthArea(true); }
                            },
                        ]
                    },
                    '-',
                    {
                        text: 'Com informações',
                        iconCls: 'icon-crgmpe icon-crgmpe-user-group',
                        scope: this,
                        handler: function() { this.getFilled(); }
                    },
                    {
                        text: 'Sem informações',
                        iconCls: 'icon-crgmpe icon-crgmpe-arrows',
                        scope: this,
                        handler: function() { this.getNoFilled(); }
                    },
                    '-',
                    {
                        text: 'Mostrar Todos',
                        iconCls: 'icon-crgmpe icon-crgmpe-list-papers',
                        scope: this,
                        handler: function() { this.getShowAllHealthArea(true); }
                    },
                ]
            });
        }
        return this._applyFilterHealthAreaAction;
    },

    getMenuHealthAreaAction: function() {
        if(!this._menuHealthAreaAction){
            this._menuHealthAreaAction = new Ext.Button({
                xtype: 'button',
                text: 'Administração',
                iconCls: 'icon-crgmpe icon-crgmpe-settings',
                hidden: true,
                menu: [
                    {
                        text: 'Enviar pesquisa',
                        iconCls: 'icon-crgmpe icon-crgmpe-send-mail',
                        scope: this,
                        handler: function() {
                            Ext._create('corregedoria.cirdir.health.healtharea.SendSearch', {
                                values: {
                                },
                            }).show();
                        }
                    },
                    '-',
                    {
                        text: 'Avaliações',
                        iconCls: 'icon-crgmpe icon-crgmpe-report-edit',
                        scope: this,
                        disabled: false,
                        menu: [
                            {
                              text: 'Painel de Administração',
                              iconCls: 'icon-crgmpe icon-crgmpe-tool',
                              scope: this,
                              handler: function() {
                                  var newtab = Ext._create('corregedoria.cirdir.health.healtharea.ManagementHealthArea', {
                                    closable: true
                                  });
                                  toolkit.Application.tabspace.add(newtab);
                                  toolkit.Application.tabspace.setActiveTab(newtab);
                              },
                            },
                        ]
                    },
                ]
            });
        }
        return this._menuHealthAreaAction;
    },

    getReportsAction: function(cfg) {
        if(!this._reportsAction){
            this._reportsAction = new Ext.Button({
                xtype: 'button',
                text: 'Relatórios',
                iconCls: 'icon-crgmpe icon-crgmpe-application-pdf',
                hidden: true,
                menu: [
                    '-',
                    {
                        text: 'Listagem de Pendências - Membros',
                        iconCls: 'icon-crgmpe icon-crgmpe-application-pdf',
                        scope: this,
                        handler: this.openMemberListPendenceReport
                    },
                    {
                        text: 'Listagem de Endereço - Membros',
                        iconCls: 'icon-crgmpe icon-crgmpe-application-pdf',
                        scope: this,
                        handler: this.openMemberAddressListReport
                    },
                    '-',
                    {
                        text: 'Listagem de Pendências - Servidores',
                        iconCls: 'icon-crgmpe icon-crgmpe-application-pdf',
                        scope: this,
                        handler: this.openEmployeePendenceReport
                    }
                ]
            });
        }
        return this._reportsAction;
    },

    openReportSubmittedAfterDeadline: function() {
        Ext._create('corregedoria.cirdir.report.SubmittedAfterDeadlineReport', {
            values: { }
        }).show();
    },

    openEmployeePendenceReport: function() {
        Ext._create('corregedoria.cirdir.report.EmployeePendenceReport', {
            values: { }
        }).show();
    },

    openEmployeeMemberPendenceReport: function() {
        Ext._create('corregedoria.cirdir.report.EmployeeMemberPendenceReport', {
            values: { }
        }).show();
    },

    openMemberListPendenceReport: function() {
        Ext._create('corregedoria.cirdir.report.MemberPendenceListReport', {
            values: { }
        }).show();
    },

    openMemberAddressListReport: function() {
        Ext._create('corregedoria.cirdir.report.MemberListAddressReport', {
            values: { }
        }).show();
    },

    openReportTeaching: function() {
        Ext._create('corregedoria.cirdir.report.TeachingReport', {
            values: { }
        }).show();
    },

    filterMember: function()  {
        this.showAll(false);
        this.addFilterProperty('employee__tipo', 'M', 201, true);
    },

    filterEmployee: function()  {
        this.showAll(false);
        this.addFilterProperty('employee__tipo', 'S', 202, true);
    },

    showAll: function(exec)  {
        this.removeFilterProperty('employee__tipo', 201, false);
        this.removeFilterProperty('employee__tipo', 202, exec);
    },

    getShowAll: function(exec) {
        this.removeFilterProperty('in_teaching__isnull', 108, false);
        this.removeFilterProperty('in_address__authorization_reside_outside', 109, false);
        this.removeFilterProperty('in_address__validate_reside_outside', 109, false);
        this.pendencyRemoveAll(exec);
    },

    getOpened: function() {
        this.getOpenedClosed(false);
        this.addFilterProperty('closed_address', false, 101, false);
        this.addFilterProperty('closed_teaching_1st_semestry', false, 101, false);
        this.addFilterProperty('closed_teaching_2nd_semestry', false, 101, false);
        this.addFilterProperty('closed_property', false, 101, false);
        this.addFilterProperty('closed_debits', false, 101, false);
        this.addFilterProperty('closed_health', false, 101, true);
    },

    getClosed: function() {
        this.getOpenedClosed(false);
        this.addFilterProperty('closed_address', true, 102, false);
        this.addFilterProperty('closed_teaching_1st_semestry', true, 103, false);
        this.addFilterProperty('closed_teaching_2nd_semestry', true, 104, false);
        this.addFilterProperty('closed_property', true, 105, false);
        this.addFilterProperty('closed_debits', true, 106, false);
        this.addFilterProperty('closed_health', true, 107, true);
    },

    getOpenedClosed: function(exec) {
        this.removeFilterProperty('closed_address', 101, false);
        this.removeFilterProperty('closed_teaching_1st_semestry', 101, false);
        this.removeFilterProperty('closed_teaching_2nd_semestry', 101, false);
        this.removeFilterProperty('closed_property', 101, false);
        this.removeFilterProperty('closed_debits', 101, false);
        this.removeFilterProperty('closed_health', 101, false);
        this.removeFilterProperty('closed_address', 102, false);
        this.removeFilterProperty('closed_teaching_1st_semestry', 103, false);
        this.removeFilterProperty('closed_teaching_2nd_semestry', 104, false);
        this.removeFilterProperty('closed_property', 105, false);
        this.removeFilterProperty('closed_debits', 106, false);
        this.removeFilterProperty('closed_health', 107, exec);
    },

    getTeaching: function() {
        this.getShowAll(false);
        this.addFilterProperty('in_teaching__isnull', false, 108, true);
    },

    getResideOutside: function() {
        this.pendencyRemoveAll(false);
        this.getShowAll(false);
        this.addFilterProperty('in_address__authorization_reside_outside', true, 109, false);
        this.addFilterProperty('in_address__validate_reside_outside', false, 109, true);
    },

    pendencyAddress: function(exec) {
        this.pendencyRemoveAll(false);
        this.addFilterProperty('pendency_address', true, 301, true);
    },

    pendencyTeaching: function() {
        this.pendencyRemoveAll(false);
        this.addFilterProperty('pendency_teaching_1st_semestry', true, 302, false);
        this.addFilterProperty('pendency_teaching_2nd_semestry', true, 302, true);
    },

    pendencyProperty: function() {
        this.pendencyRemoveAll(false);
        this.addFilterProperty('pendency_property', true, 303, true);
    },

    pendencyDebits: function() {
        this.pendencyRemoveAll(false);
        this.addFilterProperty('pendency_debits', true, 304, true);
    },

    pendencyHealth: function() {
        this.pendencyRemoveAll(false);
        this.addFilterProperty('pendency_health', true, 305, true);
    },

    pendencyAll: function() {
        this.pendencyRemoveAll(false);
        this.addFilterProperty('pendency_address', true, 306, false);
        this.addFilterProperty('pendency_teaching_1st_semestry', true, 306, false);
        this.addFilterProperty('pendency_teaching_2nd_semestry', true, 306, false);
        this.addFilterProperty('pendency_property', true, 306, false);
        this.addFilterProperty('pendency_debits', true, 306, false);
        this.addFilterProperty('pendency_health', true, 306, true);
    },

    pendencyRemoveAll: function(exec) {
        this.removeFilterProperty('pendency_address', 301, false);
        this.removeFilterProperty('pendency_teaching_1st_semestry', 302, false);
        this.removeFilterProperty('pendency_teaching_2nd_semestry', 302, false);
        this.removeFilterProperty('pendency_property', 303, false);
        this.removeFilterProperty('pendency_debits', 304, false);
        this.removeFilterProperty('pendency_health', 305, false);
        this.removeFilterProperty('pendency_address', 306, false);
        this.removeFilterProperty('pendency_teaching_1st_semestry', 306, false);
        this.removeFilterProperty('pendency_teaching_2nd_semestry', 306, false);
        this.removeFilterProperty('pendency_property', 306, false);
        this.removeFilterProperty('pendency_debits', 306, false);
        this.removeFilterProperty('pendency_health', 306, exec);
    },

    notSubmittedAddress: function() {
        this.notSubmittedRemoveAll(false);
        this.addFilterProperty('address_submitted_at__isnull', true, 401, true);
    },

    notSubmittedTeachingOne: function() {
        this.notSubmittedRemoveAll(false);
        this.addFilterProperty('teaching_1st_semestry_submitted_at__isnull', true,  404, true);
    },

    notSubmittedTeachingTwo: function() {
        this.notSubmittedRemoveAll(false);
        this.addFilterProperty('teaching_2nd_semestry_submitted_at__isnull', true, 405, true);
    },

    notSubmittedProperty: function() {
        this.notSubmittedRemoveAll(false);
        this.addFilterProperty('property_submitted_at__isnull', true, 402, true);
    },

    notSubmittedDebits: function() {
        this.notSubmittedRemoveAll(false);
        this.addFilterProperty('debits_submitted_at__isnull', true, 403, true);
    },

    notSubmittedAll: function() {
        this.notSubmittedRemoveAll(false);
        this.addFilterProperty('address_submitted_at__isnull', true, 401, false);
        this.addFilterProperty('property_submitted_at__isnull', true, 402, false);
        this.addFilterProperty('debits_submitted_at__isnull', true, 403, false);
        this.addFilterProperty('teaching_1st_semestry_submitted_at__isnull', true,  404, false);
        this.addFilterProperty('teaching_2nd_semestry_submitted_at__isnull', true, 405, true);
    },

    notSubmittedRemoveAll: function(exec) {
        this.removeFilterProperty('address_submitted_at__isnull', 401, false);
        this.removeFilterProperty('property_submitted_at__isnull', 402, false);
        this.removeFilterProperty('debits_submitted_at__isnull', 403, false);
        this.removeFilterProperty('teaching_1st_semestry_submitted_at__isnull', 404, false);
        this.removeFilterProperty('teaching_2nd_semestry_submitted_at__isnull', 405, exec);
    },

    getApplyFilterAction: function() {
        if(!this._applyFilterAction){
            this._applyFilterAction = new Ext.Button({
                xtype: 'button',
                text: 'Exibir',
                iconCls: 'icon-crgmpe icon-crgmpe-find',
                hidden: true,
                menu: [
                    {
                        text: 'Integrantes',
                        iconCls: 'icon-crgmpe icon-crgmpe-stabilization',
                        scope: this,
                        menu: [
                            {
                                text: 'Somente Membros',
                                iconCls: 'icon-crgmpe icon-crgmpe-man-black',
                                scope: this,
                                handler: function() { this.filterMember(); }
                            },
                            {
                                text: 'Somente Servidores',
                                iconCls: 'icon-crgmpe icon-crgmpe-man-blue',
                                scope: this,
                                handler: function() { this.filterEmployee(); }
                            },
                            '-',
                            {
                                text: 'Membros/Servidores',
                                iconCls: 'icon-crgmpe icon-crgmpe-user-group',
                                scope: this,
                                handler: function() { this.showAll(true); }
                            },
                        ]
                    },
                    // '-',
                    // {
                    //     text: 'Situação',
                    //     iconCls: 'icon-crgmpe icon-crgmpe-node-select',
                    //     scope: this,
                    //     menu: [
                    //         {
                    //             text: 'Abertos',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-open',
                    //             scope: this,
                    //             handler: function() { this.getOpened(); }
                    //         },
                    //         {
                    //             text: 'Fechados',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-close',
                    //             scope: this,
                    //             handler: function() { this.getClosed(); }
                    //         },
                    //         '-',
                    //         {
                    //             text: 'Mostrar todos',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-select',
                    //             scope: this,
                    //             handler: function() { this.getOpenedClosed(true); }
                    //         },
                    //     ]
                    // },
                    // '-',
                    // {
                    //     text: 'Não submetido',
                    //     iconCls: 'icon-crgmpe icon-crgmpe-waiting-decision',
                    //     scope: this,
                    //     menu: [
                    //         {
                    //             text: 'Residência',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-go-home',
                    //             scope: this,
                    //             handler: function() { this.notSubmittedAddress(); }
                    //         },
                    //         {
                    //             text: 'Docência 1° Semestre',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-book',
                    //             scope: this,
                    //             handler: function() { this.notSubmittedTeachingOne(); }
                    //         },
                    //         {
                    //             text: 'Docência 2° Semestre',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-book',
                    //             scope: this,
                    //             handler: function() { this.notSubmittedTeachingTwo(); }
                    //         },
                    //         {
                    //             text: 'Bens e Direitos',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-money',
                    //             scope: this,
                    //             handler: function() { this.notSubmittedProperty(); }
                    //         },
                    //         {
                    //             text: 'Dívidas e Ônus Reais',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-list-remove',
                    //             scope: this,
                    //             handler: function() { this.notSubmittedDebits(); }
                    //         },

                    //         '-',
                    //         {
                    //             text: 'Mostrar Todas',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-exclamation-red',
                    //             scope: this,
                    //             handler: function() { this.notSubmittedAll(true); }
                    //         },
                    //         '-',
                    //         {
                    //             text: 'Limpar filtro',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-exclamation-red',
                    //             scope: this,
                    //             handler: function() { this.notSubmittedRemoveAll(true); }
                    //         },
                    //     ]
                    // },
                    // '-',
                    // {
                    //     text: 'Exercem docência',
                    //     iconCls: 'icon-crgmpe icon-crgmpe-user-group',
                    //     scope: this,
                    //     handler: function() { this.getTeaching(); }
                    // },
                    // {
                    //     text: 'Residem fora da comarca',
                    //     iconCls: 'icon-crgmpe icon-crgmpe-arrows',
                    //     scope: this,
                    //     handler: function() { this.getResideOutside(); }
                    // },
                    // '-',
                    // {
                    //     text: 'Pendências',
                    //     iconCls: 'icon-crgmpe icon-crgmpe-exclamation-red',
                    //     scope: this,
                    //     menu: [
                    //         {
                    //             text: 'Residência',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-go-home',
                    //             scope: this,
                    //             handler: function() { this.pendencyAddress(); }
                    //         },
                    //         {
                    //             text: 'Docência',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-book',
                    //             scope: this,
                    //             handler: function() { this.pendencyTeaching(); }
                    //         },
                    //         {
                    //             text: 'Bens e Direitos',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-money',
                    //             scope: this,
                    //             handler: function() { this.pendencyProperty(); }
                    //         },
                    //         {
                    //             text: 'Dívidas e Ônus Reais',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-list-remove',
                    //             scope: this,
                    //             handler: function() { this.pendencyDebits(); }
                    //         },
                    //         {
                    //             text: 'Saúde',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-health',
                    //             scope: this,
                    //             handler: function() { this.pendencyHealth(); }
                    //         },
                    //         '-',
                    //         {
                    //             text: 'Mostrar Todas',
                    //             iconCls: 'icon-crgmpe icon-crgmpe-exclamation-red',
                    //             scope: this,
                    //             handler: function() { this.pendencyAll(true); }
                    //         },
                    //     ]
                    // },
                    // '-',
                    // {
                    //     text: 'Mostrar Todos',
                    //     iconCls: 'icon-crgmpe icon-crgmpe-list-papers',
                    //     scope: this,
                    //     handler: function() {
                    //         this.removeAllFilterPropertyLocal();
                    //     }
                    // },
                ]
            });
        }
        return this._applyFilterAction;
    },

    removeAllFilterPropertyLocal: function() {
        var oldFilter = this.getFilter();

        oldFilter.forEach(
            function(item) {
                this.removeFilterProperty(item.property, item.stage, false);
            },
            this
        );
        this.getStore().load();
    },

    openAddPeriodWindow: function(cfg) {
        Ext.Ajax.request({
            scope: this,
            url: core.callAction('CIRDIRControlInformation', 'get_lastyear'),
            callback: function() {
            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if (rst.success == true) {
                    Ext._create('corregedoria.cirdir.AddYearWindow', {
                        params: {
                          mainGrid: this,
                          lastyear: rst.lastyear,
                        },
                    }).show();
                } else {
                    Ext.Msg.show({
                        title: 'Abertura SRDIR',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
                core.invokeCallback((this.callback || {}).success);
            },
            failure: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Abertura SRDIR',
                    msg: rst.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
        });
    },

    open: function(cfg, criteria) {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            srdir_id = selected.get('pk');
        } else {
            srdir_id = '';
        }
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Abrindo SRDIR...'});
        if(selected) {
            Ext.Msg.show({
                title: 'Abertura SRDIR',
                msg: 'Tem certeza que deseja abrir o SRDIR selecionado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('CIRDIRControlInformation', 'open'),
                        callback: function() {
                            this.getStore().reload();
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Abertura SRDIR',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            } else {
                                Ext.Msg.show({
                                    title: 'Abertura SRDIR',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                            core.invokeCallback((this.callback || {}).success);
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Abertura SRDIR',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: {
                            srdir_id: srdir_id,
                            criteria: criteria,
                        },
                    });
                }
            });
        } else {
            Ext._create('corregedoria.cirdir.OpenWindow', {
                params: {
                  mainGrid: this,
                  criteria: criteria,
                },
            }).show();
        }
    },

    close: function(cfg, criteria) {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            srdir_id = selected.get('pk');
        } else {
            srdir_id = '';
        }
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Fechando SRDIR...'});
        if(selected) {
            Ext.Msg.show({
                title: 'Fechamento SRDIR',
                msg: 'Tem certeza que deseja fechar o SRDIR selecionado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('CIRDIRControlInformation', 'close'),
                        callback: function() {
                            this.getStore().reload();
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Fechamento SRDIR',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            } else {
                                Ext.Msg.show({
                                    title: 'Fechamento SRDIR',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                            core.invokeCallback((this.callback || {}).success);
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Fechamento SRDIR',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: {
                            srdir_id: srdir_id,
                            criteria: criteria,
                        },
                    });
                }
            });
        } else {
            Ext._create('corregedoria.cirdir.CloseWindow', {
                params: {
                  mainGrid: this,
                  criteria: criteria,
                },
            }).show();
        }
    },

    getMenuAction: function(cfg) {
        if(!this._menuAction){
            this._menuAction = new Ext.Button({
                xtype: 'button',
                text: 'Administração',
                iconCls: 'icon-crgmpe icon-crgmpe-settings',
                hidden: true,
                menu: [
                    {
                        text: 'Adicionar ano',
                        iconCls: 'icon-crgmpe icon-crgmpe-calendar',
                        scope: this,
                        handler: function() { this.openAddPeriodWindow(cfg);  }
                    },
                    {
                        text: 'Adicionar integrante',
                        iconCls: 'icon-crgmpe icon-crgmpe-list-add',
                        scope: this,
                        handler: function() {
                          Ext._create('corregedoria.cirdir.AddEmployeeWindow', {
                              params: {
                                mainGrid: this,
                              },
                          }).show();
                        }
                    },
                    '-',
                    {
                        text: 'Docência',
                        iconCls: 'icon-crgmpe icon-crgmpe-user-group',
                        scope: this,
                        menu: [
                            {
                                text: 'Gerenciar Horários',
                                iconCls: 'icon-crgmpe icon-crgmpe-clock',
                                scope: this,
                                handler: function() {
                                  Ext._create('corregedoria.cirdir.teaching.schedule.ManageWindow', {
                                      params: {
                                        mainGrid: this,
                                      },
                                  }).show();
                                }
                            },
                            {
                                text: 'Gerenciar Instituições',
                                iconCls: 'icon-crgmpe icon-crgmpe-go-home',
                                scope: this,
                                handler: function() {
                                  Ext._create('corregedoria.cirdir.teaching.institution.ManageWindow', {
                                      params: {
                                        mainGrid: this,
                                      },
                                  }).show();
                              }
                          },
                          {
                              text: 'Gerenciar Disciplinas',
                              iconCls: 'icon-crgmpe icon-crgmpe-report-edit',
                              scope: this,
                              handler: function() {
                                Ext._create('corregedoria.cirdir.teaching.discipline.ManageWindow', {
                                    params: {
                                      mainGrid: this,
                                    },
                                }).show();
                            }
                          }
                        ]
                    },
                    '-',
                    {
                        text: 'Remover',
                        iconCls: 'icon-crgmpe icon-crgmpe-delete',
                        scope: this,
                        handler: function() {
                            Ext._create('corregedoria.cirdir.DeleteWindow', {
                                params: {
                                  mainGrid: this,
                                },
                            }).show();
                        }
                    },
                    '-',
                    {
                        text: 'Agendar ações',
                        iconCls: 'icon-crgmpe icon-crgmpe-calendar-plus',
                        scope: this,
                        handler: function() {
                            Ext._create('corregedoria.cirdir.ScheduleActionsWindow', {
                                params: {
                                  mainGrid: this,
                                },
                            }).show();
                        }
                    },
                    '-',
                    {
                        text: 'Log Privado',
                        iconCls: 'icon-crgmpe icon-crgmpe-detalhes',
                        scope: this,
                        handler: function() {
                            var selected = this.getSelectionModel().getSelected();
                            if (selected) {
                                Ext._create('corregedoria.cirdir.PrivateLogWindow', {
                                    params: {
                                        controlinformation: selected.get('pk'),
                                        employee: selected.get('employee_unicode'),
                                        mainGrid: this,
                                    },
                                }).show();
                            } else {
                                Ext.Msg.show({
                                    title: 'Log Privado',
                                    msg: 'Selecione um SRDIR para registro do Log Privado',
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        }
                    },
                ]
            });
        }
        return this._menuAction;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 150, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Servidor', dataIndex: 'employee_unicode', id: 'autoExpandColumn'},
                    {header: 'Ano', dataIndex: 'year', width: 70},
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                columnAction: false
            }
        );
        corregedoria.cirdir.Grid.superclass.constructor.call(this, cfg);
    }
});
core.RestfulGrid.register(
    'corregedoria.cirdir.Restful',
    'corregedoria.cirdir.Grid'
);
