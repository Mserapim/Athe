Ext._define('judicial.OutCourtLawsuitGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.OutCourtLawsuitWindow',

    showContextMenu: false,

    singleton: {
        _introductionDB: [],

        introductionRegister: function(title, icon, klass, values) {
            var filtred = judicial.OutCourtLawsuitGrid._introductionDB.filter(
                function(reg) {
                    return (reg.text === title);
                }
            );

            if(filtred.length === 0)
                judicial.OutCourtLawsuitGrid._introductionDB.push({
                    text: title,
                    icon: icon,
                    klass: klass,
                    values: values
                });

            if(DEBUG) console.log('introduction register for %s', title);
        },

        introductionSubMenu: function(scope, params) {
            var submenu = [];
            var context = null;
            judicial.OutCourtLawsuitGrid._introductionDB.forEach(
                function(i) {
                    if(context && context != i.klass)
                        submenu.push('-');

                    context = i.klass;

                    submenu.push({
                        text: i.text,
                        icon: i.icon,
                        handler: function() {
                            if(scope.getParams().location){
                                var wnd = Ext._create(i.klass, {
                                    action: 'create',
                                    params: {
                                        location: scope.getParams().location
                                    },
                                    values: i.values,
                                    callback: {
                                        success: {
                                            scope: (scope || window),
                                            fn: function() {
                                                this.getStore().reload();
                                            }
                                        }
                                    }
                                });

                                wnd.show();
                            }else{
                                Ext.Msg.show({
                                    title: 'Instaurar procedimento',
                                    msg: 'Por favor, selecione uma lotação.',
                                    buttons: Ext.Msg.OK,
                                    icon: Ext.Msg.INFO,
                                });
                            }
                        }
                    });
                }
            );

            return submenu;
        }
    },

    configOrderToolBar: ['openDocument', '-', 'introduction', 'followDeadline', 'protocolImport', '-', 'bookmarker', '-', 'search', '->', 'download'],

    filterWithoutActingZone: function(item, checked) {
        if(checked)
            this.setFilterProperty('acting_zone', null, 3001);
        else
            this.removeFilterProperty('acting_zone', 3001);
    },

    getBookmarkerAction: function(cfg) {
        if(!this._bookemarkerAction)
            this._bookemarkerAction = Ext._create('Ext.Button', {
                text: 'Localizador',
                iconCls: 'icon-judicial icon-ejud-open-bookmark',
                scope: this,
                handler: this.openTagManageWindow
            });

        return this._bookemarkerAction;
    },

    openTagManageWindow: function() {
        var params = {};
        var selections = this.getSelectionModel().getSelections();

        if(this.getParams().location)
            params.work_place = this.getParams().location;

        if(selections.length > 0)
            params.lawsuit = selections.map(function(data) { return data.get('pk'); });

        params.tag_type = 2;

        Ext._create('judicial.TagManageWindow', {
            params: params,
            success: {
                scope: this,
                fn: function() {
                    this.getStore().reload();
                }
            }
        }).show();
    },

    getIntroductionAction: function(cfg) {
        if(!this._introductionAction)
            this._introductionAction = Ext._create('Ext.Button', {
                iconCls: 'icon-core icon-core-add',
                text: 'Instaurar Procedimento',
                menu: judicial.OutCourtLawsuitGrid.introductionSubMenu(this, this.getParams())
            });

        return this._introductionAction;
    },

    getProtocolImportAction: function(cfg) {
        if(!this._protocolImportAction)
            this._protocolImportAction = Ext._create('Ext.Button', {
                text: 'Importar e-Doc',
                iconCls: 'icon-judicial icon-ejud-protocol',
                scope: this,
                handler: this.openProtocolImport
            });

        return this._protocolImportAction;
    },

    openProtocolImport: function() {
        Ext._create('judicial.ProtocolImportWindow', {
            params: this.getParams(),
            success: {
                scope: this,
                fn: function() {
                    this.getStore().reload();
                }
            }
        }).show();
    },

    getIntroductionOfOfficeAction: function(cfg) {
        if(!this._introductionOfOfficeAction)
            this._introductionOfOfficeAction = Ext._create('Ext.Button', {
                text: 'Notícia de Fato',
                iconCls: 'icon-judicial icon-ejud-em-instauracao-in-grid',
                scope: this,
                handler: this.openIntroductionOfOffice
            });

        return this._introductionOfOfficeAction;
    },

    openIntroductionOfOffice: function() {

        var wnd = Ext._create('judicial.parts.AssessmentNoticeOfficeWindow', {
            modal: true,
            action: 'create',
            params: {
                location: this.getParams().location
            },
            callback: {
                success: {
                    scope: this,
                    fn: function() {
                        this.getStore().reload();
                    }
                }
            }
        }).show();
    },

    getFollowDeadlineAction: function(cfg) {
        if(!this._openFollowDeadlineAction)
            this._openFollowDeadlineAction = Ext._create('Ext.Button', {
                text: 'Acompanhamento',
                iconCls: 'icon-judicial icon-ejud-outlawcortsuit-not-have-time',
                scope: this,
                handler: this.openFollowDeadline
            });

        return this._openFollowDeadlineAction;
    },

    classLawsuitGrid: function() {
        return 'judicial.OutCourtLawsuitGrid';
    },

    classLawsuitRest: function() {
        return 'judicial.OutCourtLawsuitRestful';
    },

    openFollowDeadline: function() {
        var params = {};
        var selected = this.getSelectionModel().getSelected();

        if(this.getParams().location) params.location = this.getParams().location;
        if(this.getParams().type_lawsuit) params.type_lawsuit = this.getParams().type_lawsuit;
        if(selected) params.lawsuit = selected.get('pk');

        if (!this.gridCollaboration)
            Ext._create('judicial.diligences.ExecutionOrganWindow', {
                modal: true,
                params: params,
                classLawsuitGrid: this.classLawsuitGrid(),
                classLawsuitRest: this.classLawsuitRest(),
                width: (Ext.getBody().getBox().width * 0.9),
                height: (Ext.getBody().getBox().height * 0.9)
            }).show();
        else
            Ext.Msg.show({
                title: 'Acompanhamento',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK,
                msg: 'O acompanhamento deve ser acessado do seu órgão de lotação'
            });
    },

    getOpenDocumentAction: function(cfg) {
        if(!this._openDocumentAction)
            this._openDocumentAction = Ext._create('Ext.Button', {
                text: 'Abrir Procedimento',
                iconCls: 'icon-judicial icon-ejud-open-proccess',
                scope: this,
                handler: this.validateOpenDocument
            });

        return this._openDocumentAction;
    },

    documentPath: function(selected) {
        if(this.documentMode)
            return [this.documentMode, this.forExecutionOrgan, selected.get('pk')].join('/');
        else
            return selected.get('pk');
    },

    openDocument: function() {
        var selected = this.getSelectionModel().getSelected();
        var width, height, left, top;

        width = (Ext.getBody().getBox().width * 0.9);
        height = (Ext.getBody().getBox().height * 0.9);
        left = screenX + (screen.width / 2) - (width / 2);
        top = (screen.height / 2) - (height / 2);

        var spec = [
            'width=' + width,
            'height=' + height,
            'top=' + top,
            'left=' + left,
            'scrollbars',
            'resizable',
            'status',
            'titlebar'
        ];

        if(this._wndP) this._wndP.close();

        this._wndP = window.open(
            '/athenas/EJudOutCourtLawsuit/viewer/#' + this.documentPath(selected),
            'ejud-proccess',
            spec.join(', ')
        );

        if(!this._wndP)
            Ext.Msg.show({
                title: 'Abrindo procedimento!',
                msg: 'O bloqueador de popup interceptou a abertura do procedimento!',
                buttons: Ext.Msg.OK,
                icons: Ext.Msg.ERROR
            });

        this._wndP.config = function() {
            return selected.data;
        };

        this._wndP.MainRemoteObserver = core.RemoteObserver;
        this._wndP.getRemoteObserver = function() { return core.RemoteObserver; };
    },

    validateOpenDocument: function() {
        var selected = this.getSelectionModel().getSelected();

        if (!selected.get('is_received')) {
            Ext.Msg.show({
                title: 'Abrir Procedimento',
                msg: 'Deseja abrir/receber este Procedimento?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    switch(btn) {
                        case 'yes':
                            this.openDocument();
                            break;
                        case 'no':
                            return;
                    }
                }
            });
        } else if(selected.get('in_give_back_box')) {
            console.log('nao pense que meu coração é de papel')
            this.removeLawsuitTag(selected.get('pk'), 'proc-devolvidos');
            this.openDocument();
        } else {
            this.openDocument();
        }
    },

    updateItem: function() {
        this.validateOpenDocument();
    },

    deadlineRenderer: function(value, cell, data) {
        var message;
        if(value == 0){
            value = 'Último dia';
        } else {

            if (value == 1)
                message = 'Resta';
            else if (value > 1)
                message = 'Restam';
            else if (value < 0) {
                message = 'Atrasado em';
                value *= (-1);
            }

            if (!value && data.get('closed'))
                value = 'Finalizado';
            else if (!value && value !== 0)
                value = 'Suspenso ou sem prazo definido';
            else
                value = [message, value, (value > 1 ? 'dias' : 'dia')].join(' ');
        }

        return '<div>' + value + '</div>';
    },

    formatCacheNumberUrgent: function(value, metaData, record, rowIndex, colIndex, store) {
        var reminderTitles = record.get('titles_reminders');
        var countReminder = reminderTitles.length;

        if(countReminder > 0){
            reminders = countReminder > 9 ? '+9' : countReminder;
            value += ' <span class="badge badge-warning" ext:qtip="' + reminderTitles.join('<br/>') + '">'+ reminders +'</span>';
        }

        if(record.get('urgent')){
            value += ' <span class="badge badge-important">!</span>';
        }

        return value;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 90,
                        menuDisabled: true,
                        renderer: core.rendererIconGrid,
                        hidden: true
                    },
                    {sortable: true, header: 'Código', dataIndex: 'origin_codigo', width: 120, hidden: true},
                    {sortable: false, header: 'Interessado', dataIndex: 'origin_interessado_unicode', width: 200},
                    {sortable: true, header: 'Procedimento', renderer: this.formatCacheNumberUrgent, dataIndex: 'cache_number', width: 150},
                    {sortable: true, header: 'Título', dataIndex: 'title', id: 'autoExpandColumn'},
                    {sortable: false, header: 'Fim do Prazo', dataIndex: 'deadline', width: 125, renderer: this.deadlineRenderer},
                    {sortable: true, header: 'Tipo do Procedimento', dataIndex: 'type_lawsuit_display', width: 165},
                    {sortable: true, header: 'Área de atuação', dataIndex: 'acting_zone_unicode', width: 165},
                    {sortable: true, header: 'Localização', dataIndex: 'current_location_unicode', width: 90},
                    {sortable: false, header: 'Último Movimento', dataIndex: 'last_document_signed', width: 300},
                    {sortable: true, header: 'Data do Movimento', dataIndex: 'date_last_document_signed', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {sortable: true, header: 'Na Casa', dataIndex: 'location_unicode', width: 325, hidden: true},
                    {sortable: true, header: 'Ano', dataIndex: 'year', width: 90, hidden: true},
                    {sortable: true, header: 'Número', dataIndex: 'number_lawsuit', width: 90, hidden: true}
                ]
            );

        return this._columnModel;
    },

    filterMovement: function() {
        Ext._create(
            'judicial.outcourtlawsuit.FilterMovementWindow',
            {grid: this}
        ).show();
    },

    filterBloke: function () {
        Ext._create(
            'judicial.outcourtlawsuit.FilterBlokeWindow',
            { grid: this }
        ).show();
    },

    getFilterMenu: function() {
        if(!this._filterMenu)
            this._filterMenu = [
                {
                    text: 'Por último Movimento',
                    scope: this,
                    handler: this.filterMovement
                },
                '-',
                {
                    text: 'Por Investigado/Apontado',
                    scope: this,
                    handler: this.filterBloke
                },
                '-',
                {
                    text: 'Somente sem área de atuação',
                    hideOnClick: false,
                    checked: false,
                    listeners: {
                        scope: this,
                        checkchange: this.filterWithoutActingZone
                    }
                }
            ];

        return this._filterMenu;
    },

    doDownload: function() {
        var config = {
            filter: Ext.encode(this.getFilter()),
            keyword: this.getKeywordField().getValue(),
            start: 0,
            limit: this.getStore().getTotalCount(),
            format: 'text/csv',
            defaultRoute: this.storeDefaultRoute !== undefined ? this.storeDefaultRoute : 'default',
            execution_organ: this.forExecutionOrgan !== undefined ? this.forExecutionOrgan : 0
        };
        var rest = this.factoryRestful();
        var url = rest.getRoute('export').url + '?' + Ext.urlEncode(config);

        window.open(url, '_self');
    },

    markWithTag: function(oidOutCourtLawSuit, oidTag, checked, menuContext) {
        var mask = new Ext.LoadMask(this.ownerCt.getEl(), {msg: 'Atualizando procedimento...'});
        mask.show();
        this.factoryRestful().markWithTag(
            oidOutCourtLawSuit,
            oidTag,
            checked,
            {
                scope: this,
                fn: function(result){
                    if(!menuContext)
                        Ext.Msg.show({
                            title: 'Atualizando procedimento.',
                            icon: result.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                            msg: result.message,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(result){
                    Ext.Msg.show({
                        title: 'Atualizando Procedimento',
                        msg: 'Recurso indisponivel no momento.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function(result){
                    mask.hide()
                    this.getStore().reload();
                }
            }
        );
    },

    markForExecutionInSecretary: function (lawsuits, menuContext) {
        var mask = new Ext.LoadMask(this.ownerCt.getEl(), { msg: 'Atualizando procedimento...' });
        mask.show();
        this.factoryRestful().markForExecutionInSecretary(
            lawsuits,
            {
                scope: this,
                fn: function (result) {
                    if (!menuContext)
                        Ext.Msg.show({
                            title: 'Atualizando procedimentos.',
                            icon: result.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                            msg: result.message,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function (result) {
                    Ext.Msg.show({
                        title: 'Atualizando Procedimentos',
                        msg: result,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function (result) {
                    mask.hide()
                    this.getStore().reload();
                }
            }
        );
    },

    removeLawsuitTag: function (lawsuits, tag) {
        var mask = new Ext.LoadMask(this.ownerCt.getEl(), { msg: 'Atualizando procedimento...' });
        mask.show();
        this.factoryRestful().removeLawsuitTag(
            lawsuits,
            tag,
            {
                scope: this,
                fn: function (result) {}
            },
            {
                scope: this,
                fn: function (result) {
                    Ext.Msg.show({
                        title: 'Atualizando Procedimentos',
                        msg: result,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function (result) {
                    mask.hide()
                    this.getStore().reload();
                }
            }
        );
    },

    getDefaultItemsContextMenu: function(){
        var menu = [
            {
                text: 'Abrir Procedimento',
                iconCls: 'icon-judicial icon-ejud-open-proccess',
                scope: this,
                handler: this.validateOpenDocument
            },
            {
                text: 'Acompanhamento',
                iconCls: 'icon-judicial icon-ejud-outlawcortsuit-not-have-time',
                scope: this,
                handler: this.openFollowDeadline
            },
            {
              text: 'Solicitar Colaboração',
              iconCls: 'icon-judicial icon-ejud-manifestation-indirect',
              scope: this,
              handler: this.openRequestCollaborationWindow,
            },
            {
              text: 'Lembretes',
              iconCls: 'icon-core icon-core-balloons',
              scope: this,
              handler: this.openReminderWindow,
            },
            {
              text: 'Relatório de Atuações em Procedimento',
              iconCls: 'icon-core icon-core-reports',
              scope: this,
              handler: this.generateReportActivity,
            },
            '-',
            {
                text: 'Enviar para a secretaria',
                iconCls: 'icon-judicial icon-judicial icon-ejud-triage-effectivate',
                scope: this,
                handler: this.forExecutionInSecretary,
            },
            {
                text: 'Retirar da secretaria',
                iconCls: 'icon-judicial icon-judicial icon-ejud-give-back-diligence',
                scope: this,
                handler: this.giveBackExecutionOrgan,
            }
        ];

        return menu;

    },

    generateReportActivity: function() {
        var selections = this.getSelectionModel().getSelections();
        if(selections.length > 0) {
            var value = selections.map(function(data) { return data.get('pk'); })[0];

            engine.mq.Report.request({
                report: '/to/mpe/judicial/activity_report',
                waitMessage: 'Gerando relatório...',
                params: {
                    report_name: 'Relatório de Atuações em Procedimento',
                    outfile: 'relatorio-de-atuacoes-em-procedimento.pdf',
                    outcourtlawsuit: value
                }
            });
        }
        else
          Ext.Msg.show({
              title: 'Ação não permitida',
              msg: 'Selecione um procedimento para geração do relatório.',
              icon: Ext.Msg.INFO,
              buttons: Ext.Msg.OK
          });
    },

    openRequestCollaborationWindow: function() {
        var selections = this.getSelectionModel().getSelections();
        if(selections.length > 0) {
            lawsuit = selections.map(function(data) { return data.get('pk'); })[0];
            is_received = selections.map(function(data) { return data.get('is_received'); })[0];
            origin_location = selections.map(function(data) { return data.get('location'); })[0];
        }
        if(is_received)
          Ext._create('judicial.requestcollaboration.WindowManage', {
              modal: true,
              params: {
                  lawsuit: lawsuit,
                  origin_location: origin_location
              }
          }).show();
        else
          Ext.Msg.show({
              title: 'Ação não permitida',
              msg: 'Não é possivel solicitar colaboração para um procedimento que ainda não foi recebido.' +
               'Receba o procedimento para solicitar a colaboração',
              icon: Ext.Msg.INFO,
              buttons: Ext.Msg.OK
          });
    },

    forExecutionInSecretary: function () {
        var selections = this.getSelectionModel().getSelections();
        var lawsuits = selections.map(function (data) { return data.get('pk'); })
        this.markForExecutionInSecretary(lawsuits, true);
    },

    giveBackExecutionOrgan: function () {
        var selections = this.getSelectionModel().getSelections();
        var lawsuits = selections.map(function (data) { return data.get('pk'); })
        this.markGiveBackExecutionOrgan(lawsuits, true);
    },

    markGiveBackExecutionOrgan: function (lawsuits, menuContext) {
        var mask = new Ext.LoadMask(this.ownerCt.getEl(), { msg: 'Atualizando procedimento...' });
        mask.show();
        this.factoryRestful().markGiveBackExecutionOrgan(
            lawsuits,
            {
                scope: this,
                fn: function (result) {
                    if (!menuContext)
                        Ext.Msg.show({
                            title: 'Atualizando procedimentos.',
                            icon: result.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                            msg: result.message,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function (result) {
                    Ext.Msg.show({
                        title: 'Atualizando Procedimentos',
                        msg: result,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function (result) {
                    mask.hide()
                    this.getStore().reload();
                }
            }
        );
    },

    openReminderWindow: function() {
        var selections = this.getSelectionModel().getSelections();
        if(selections.length > 0) {
            lawsuit = selections.map(function(data) { return data.get('pk'); })[0];
            is_received = selections.map(function(data) { return data.get('is_received'); })[0];
        }
        if(is_received)
          Ext._create('judicial.reminder.lawsuit.WindowManage', {
              modal: true,
              params: {
                  lawsuit: lawsuit
              }
          }).show();
        else
          Ext.Msg.show({
              title: 'Ação não permitida',
              msg: 'Não é possivel adicionar um lembrete para um procedimento que ainda não foi recebido.' +
               'Receba o procedimento para adicionar o lembrete',
              icon: Ext.Msg.INFO,
              buttons: Ext.Msg.OK
          });
    },

    getRowContextMenu: function(toAppend) {
        this._rowContextMenu = Ext._create('Ext.menu.Menu', {
            items: this.getDefaultItemsContextMenu().concat(toAppend),
        });

        return this._rowContextMenu;
    },

    openNewTagWindow: function() {
        var item = this.getSelectionModel().getSelected();
        Ext._create('judicial.TagWindow', {
            action: 'create',
            disableSaveAndNew: true,
            values: {
                work_place: this.getParams().location,
                tag_type: '2'
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(tag) {
                        this.markWithTag(item.id, tag.pk, true);
                    }
                }
            }
        }).show();
    },

    _buildContextMenu: function(selection, xy) {
        var selected = selection[0];
        var tags = Ext._create('judicial.TagRestful');
        var items = [
            {
                text: 'Novo Localizador',
                iconCls: 'icon-core icon-core-add',
                scope: this,
                handler: this.openNewTagWindow
            }
        ];

        function factory(item, selected, scope) {
            return {
                text: item.title,
                checked: item.checked,
                hideOnClick: false,
                data: item.pk,
                listeners: {
                    scope: scope,
                    checkchange: function (menu, checked) {
                        this.markWithTag(selected.get('pk'), menu.data, checked, true);
                    }
                }
            };
        }

        function factoryUrgency(scope, selected) {
            return {
                text: 'Marcar como urgente',
                checked: selected.get('urgent'),
                listeners: {
                    scope: scope,
                    checkchange: function (menu, checked) {
                        this.markWithTag(selected.get('pk'), menu.data, checked, true);
                    }
                }
            }
        }

        function doShowContextMenu(scope) {
            var ctxMenu = scope.getRowContextMenu([
                '-',
                factoryUrgency(scope, selected),
                '-',
                {
                    text: 'Ações em bloco',
                    menu: [
                        {
                            text: 'Finalizar',
                            scope: scope,
                            handler: function() {
                                var selections = this.getSelectionModel().getSelections();
                                Ext._create('judicial.parts.batch.ArchivementWindow', {
                                    title: 'Finalização de procedimentos em bloco',
                                    action: 'create',
                                    autoCreate: false,
                                    ownerGrid: scope,
                                    params: {
                                        location: this.getParams().location,
                                        lawsuits: selections.map(function (row) { return row.get('pk'); })
                                    }
                                }).show();
                            }
                        },
                        {
                            text: 'Encaminhamento Interno',
                            scope: scope,
                            handler: function () {
                                var selections = this.getSelectionModel().getSelections();
                                Ext._create('judicial.parts.batch.RemittanceInternalWindow', {
                                    title: 'Encaminhamento de procedimentos à órgão interno',
                                    action: 'create',
                                    autoCreate: false,
                                    ownerGrid: scope,
                                    params: {
                                        location: this.getParams().location,
                                        lawsuits: selections.map(function (row) { return row.get('pk'); })
                                    }
                                }).show();
                            }
                        },
                        {
                            text: 'Encaminhamento Externo',
                            scope: scope,
                            handler: function () {
                                var selections = this.getSelectionModel().getSelections();
                                Ext._create('judicial.parts.batch.RemittanceExternalWindow', {
                                    title: 'Encaminhamento de procedimentos à órgão externo',
                                    action: 'create',
                                    autoCreate: false,
                                    ownerGrid: scope,
                                    params: {
                                        location: this.getParams().location,
                                        lawsuits: selections.map(function (row) { return row.get('pk'); })
                                    }
                                }).show();
                            }
                        }
                    ]
                },
                {
                    text: 'Movimentações em bloco',
                    menu: [
                        {
                            text: 'Movimentação Geral',
                            scope: scope,
                            handler: function () {
                                var selections = this.getSelectionModel().getSelections();
                                Ext._create('judicial.parts.batch.GeneralMotionWindow', {
                                    action: 'create',
                                    autoCreate: false,
                                    ownerGrid: scope,
                                    params: {
                                        location: this.getParams().location,
                                        lawsuits: selections.map(function (row) { return row.get('pk'); })
                                    }
                                }).show();
                            }
                        }
                    ]
                },
                {
                    text: 'Localizadores',
                    menu: items
                },
                '-',
                {
                    text: 'Marcadores estatistícos',
                    scope: scope,
                    handler: function() {
                        var selections = this.getSelectionModel().getSelections();

                        if (selections.length > 0) {
                            Ext._create('judicial.statisticMarker.OutCourtLawsuitManage', {
                                modal: true,
                                selected: selections.map(function (row) { return row.get('pk'); })
                            }).show();
                        } else {
                            Ext.Msg.show({
                                title: 'Marcadores estatisticos',
                                msg: 'Primeiro selecione um procedimento para poder manipular seus marcadores estatisticos.',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    }
                }
            ]);

            ctxMenu.showAt(xy);
        }

        tags.getTagsContextLocation(
            this.getParams().location,
            selection[0].get('pk'),
            {
                scope: this,
                fn: function(rst) {
                    var me = this;

                    (rst.tags.length > 0) && items.push('-');

                    items = items.concat(
                        rst.tags
                            .map(function(item) { return factory(item, selected, me); })
                    );

                    doShowContextMenu(this);
                }
            }
        );
    },

    buildContextMenu: function(selection, xy) {
        if (selection.length >= 1) {
            this._buildContextMenu(selection, xy);
            return true;
        }

        return false;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                viewConfig: {
                    getRowClass: function(record, rowIndex, rp, ds){
                        var classes = ['grid-line-height-150'];

                        if(!record.get('is_received'))
                            classes.push('grid-row-bold');

                        if(record.get('in_secretary')){
                            classes.push('grid-row-secretary');
                        }

                        if(record.data.deadline >= 0 && record.data.deadline < 7)
                            classes.push('x-grid3-yellow-simple');
                        else if(record.data.deadline < 0)
                            classes.push('x-grid3-red-simple');

                        return classes.join(' ');
                    }
                }
            }
        );

        judicial.OutCourtLawsuitGrid.superclass.constructor.call(this, cfg);

        if (this.showContextMenu) {
            this.on({
                scope: this,
                rowcontextmenu: function (me, index, evt) {
                    var selections = this.getSelectionModel().getSelections();

                    if (this.buildContextMenu(selections, evt.getXY())) {
                        evt.stopEvent();
                    }
                }
            });
        }
    }
});

core.RestfulGrid.register(
    'judicial.OutCourtLawsuitRestful',
    'judicial.OutCourtLawsuitGrid'
);
