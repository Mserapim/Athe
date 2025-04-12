/**
 *
 */

if(typeof(toolkit) == "undefined") {
    var toolkit = {};
}

if(typeof(CONTEXT) == "undefined") {
    console.error("Bug: O Contexto não foi definido.");
    CONTEXT = "";
}

var global = {
    Context : CONTEXT
};

/**
 * Pacote util da toolkit
 */
toolkit.util = {

    slugify: function(str) {
        str = str.replace(/^\s+|\s+$/g, ''); // trim
        str = str.toLowerCase();

        // remove accents, swap ñ for n, etc
        var from = "àáäâèéëêìíïîòóöôùúüûñç·/_,:;";
        var to   = "aaaaeeeeiiiioooouuuunc------";
        for (var i=0, l=from.length ; i<l ; i++) {
            str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
        }

        str = str.replace(/[^a-z0-9 -]/g, '') // remove invalid chars
            .replace(/\s+/g, '-') // collapse whitespace and replace by -
            .replace(/-+/g, '-'); // collapse dashes

        return str;
    },

    toIn: function(a) {
        var o = {};

        Ext.each(a, function(item) { o[item] = ''; });

        return o;
    },

    action: function(ctrl, act, args)
    {
        if (ctrl.indexOf('/') != -1)
        {
            args = ctrl.split('/');
            ctrl = args.splice(0, 1);
            act = args.splice(0, 1);
        }
        return toolkit.util.Normalize.controller_action(ctrl, act, args);
    },

    markFormErrors: function(errors, form)
    {
        errors = errors || [];
        Ext.each(errors, function(item)
            {
                var field = form.findField(item.name);
                if(field)
                    field.markInvalid(item.msgs[0]);
            }
        );
    },

    messageDialog: function(title, message)
    {
        Ext.Msg.show({
            minWidth: 300,
            maxWidth: 450,
            title: title,
            msg: message,
            buttons: Ext.MessageBox.OK
        });
    },

    errorDialog: function(message, errors, form)
    {
        var err = [];
        errors = errors || [];
        message = message || '';
        Ext.each(errors, function(item)
            {
                var field = form.findField(item.name);
                if(field)
                {
                    var msg = '<strong>' + field.fieldLabel + '</strong>: ' + item.msgs[0].toLowerCase();
                    err[err.length] = {tag: 'li', html: msg};
                }
            }
        );

        toolkit.util.markFormErrors(errors, form);
        toolkit.util.messageDialog(
            'Erro',
            Ext.DomHelper.markup({
                tag: 'div', cls: 'error-dialog',
                children: [
                    {tag: 'p', html: message},
                    {tag: 'ul', children: err}
                ]
            })
        );
    },

    replaceAll: function(subject, search_for, replace_for)
    {
        if(subject && search_for)
        {
            if(!replace_for)
                replace_for = '';

            if(Ext.isString(search_for))
            {
                arr = {};
                arr[search_for] = replace_for;
                search_for = arr;
            }

            for(key in search_for)
            {
                subject = subject.replace(key, search_for[key]);
                if(subject.indexOf(key) > -1)
                    subject = toolkit.util.replaceAll(subject, key, search_for[key]);
            }
        }
        return subject;
    },

    str2Date: function(value, format){
        /*Retorna um date de acordo com a string e format de string passados
         **/
        if(value){
            var d = value.split('/');
            return new Date(d[2],d[1]-1,d[0]);
        }else return new Date();
    },

    formatCurrency: function(value) {
        if(value == '-'){ return value; }
        
        value = core.nullValue(value, 0);
        return '<div style="text-align:right">' + Ext.util.Format.number(value, '0.0,00/i') + '</div>';
    },

    formatPercent: function(value) {
        value = core.nullValue(value, 0);
        return '<div style="text-align:right">' + Ext.util.Format.number(value, '0.0,00/i') + '%</div>';
    },

    formatBoolean: function(value){
        return value ? 'SIM' : 'NÃO'
    },

    /*Retorna um html com os icones (label e alt atributos inclusos) para o array de configurações de entrada
     *@param array_status: array com os estados a serem representado como um ícone. Cada status no array deve conter
     *       uma chave 'icon' com o valor sendo o nome do icone (ex.: teste.png) e opcionalmente uma chave 'title' e 'alt'
     *       para alimentar os respectivos tags HTML de uma imagem.
     *       Ex.: [{"icon": "add.png"},{"icon": "del.png", "title": "Remover este objeto", "alt": "Remover"}]
     **/
    formatStatus: function(value, extraCls) {
        var r;
        if(value){
            var tpl = new Ext.XTemplate(
                '<tpl for=".">',
                    '<tpl if="values.iconCls">',
                        '<div class="tk-grid-icon-cell {iconCls} {extraCls}" ext:qtip="{title}"></div>',
                    '</tpl>',
                    '<tpl if="values.icon">',
                        '<img style="margin: 1px 0 0 2px; padding:0;" src="{icon}" width="16" alt="{alt}" ext:qtip="{title}"/>',
                    '</tpl>',
                '</tpl>'
            );

            value = core.nullValue(value, []);

            if(extraCls !== undefined && Ext.isArray(value))
                value = value.map(function(item) {
                    Ext.applyIf(item, {extraCls: extraCls, title:item.alt});
                    return item;
                });

            if(Ext.isString(value))
                r = tpl.apply(Ext.decode(value));
            else
                r = tpl.apply(value);
        }
        return r;
    },

    formatLinks: function(value) {
        var tpl = new Ext.XTemplate(
            '<tpl for=".">',
                '<tpl if="link==\'\'">',
                '<img style="margin: 1px 0 0 2px; padding:0;" src="{icon}" width="16" alt="{alt}" ext:qtip="{title}"/>',
                '</tpl>',
                '<tpl if="link!=\'\'">',
                '<a href="{link}"><img style="margin: 1px 0 0 2px; padding:0;" src="{icon}" width="16" alt="{alt}" ext:qtip="{title}"/></a>',
                '</tpl>',
            '</tpl>'
        );

        var r;

        if(Ext.isString(value))
            r = tpl.apply(Ext.decode(value));
        else
            r = tpl.apply(value);

        return r;
    },

    /*Retorna um html com os icones (label e alt atributos inclusos) para o array de configurações de entrada
     *@param array_status: array com os estados a serem representado como um ícone. Cada status no array deve conter
     *       uma chave 'icon' com o valor sendo o nome do icone (ex.: teste.png) e opcionalmente uma chave 'title' e 'alt'
     *       para alimentar os respectivos tags HTML de uma imagem.
     *       Ex.: [{"icon": "add.png"},{"icon": "del.png", "title": "Remover este objeto", "alt": "Remover"}]
     **/
    formatStatusLabel: function(value) {
        var tpl = new Ext.XTemplate(
            '<tpl for=".">',
                '<span ext:qtip="{alt}" style="display: table;margin: 0; padding: 2px; padding-left:20px; background: url({icon}) no-repeat 0 center">{title}</span>',
            '</tpl>'
        );

        var r;

        if(Ext.isString(value))
            r = tpl.apply(Ext.decode(value));
        else
            r = tpl.apply(value);


        return r;
    },

    formatIconYesNo: function(value) {
        if(value == 'true' || value == true){
            return '<tpl if="value == true">' +
                '<div class="tk-grid-icon-cell icon-core icon-core-success" ext:qtip="Sim" ext:qwidth="16"></div>'+
            '</tpl>';
        }else{
            return '<tpl if="value == false">' +
                '<div class="tk-grid-icon-cell icon-core icon-core-delete" ext:qtip="Não" ext:qwidth="16"></div>'+
            '</tpl>';
        }
    },

    formatIconYesNoObj: function(value) {
        value = core.nullValue(value, false);
        if (value != undefined && value != '' && value != false)
            value = true;
        var tpl = new Ext.XTemplate(
            '<tpl if="value == true">' +
                '<div class="tk-grid-icon-cell icon-core icon-core-success" ext:qtip="Sim" ext:qwidth="16"></div>'+
            '</tpl>' +
            '<tpl if="value == false">' +
                '<div class="tk-grid-icon-cell icon-core icon-core-delete" ext:qtip="Não" ext:qwidth="16"></div>'+
            '</tpl>');
        return tpl.apply({'value': value});
    },

    rendererIconGrid: function(value) {
        var tpl = new Ext.XTemplate('<div class="tk-grid-icon-cell {iconCls}" ext:qtip="{title}" <tpl if="width">ext:qwidth="{width}</tpl>"></div>');
        var out = '';

        Ext.each(value, function(item) {
            if(item)
                out += tpl.apply({
                    'iconCls': item.iconCls,
                    'title': item.title,
                    'width': (item.width ? item.width : false)
                });
        });

        return out;
    },

    extractMinuteFormat: function(value) {
        if(!value)
            value = '0.0';
        value = value / 60;
        value = value.toString().split('.');
        var hour = value[0];
        var minute = '';
        if(value[1] != undefined)
            minute = ((value[1] * 0.60).toFixed()).toString().slice(0, 2);
        hour = hour.padStart(2, '0');
        minute = minute.padStart(2, '0');
        value = hour + ':' + minute;
        return value;
    },

    rendererMinute: function(value) {
        value = toolkit.util.extractMinuteFormat(value);
        var tpl = new Ext.XTemplate('<div><p>{value}</p></div>');
        return tpl.apply({'value': value});
    },

    downloadFromURL: function(url, id){
        var idFrame = (id ? id : 'downloadIframe');
        try{
            Ext.destroy(Ext.get(idFrame));
        }catch(e){
            console.debug('Sem iframe...');
        }
        Ext.DomHelper.append(document.body, {
            tag: 'iframe',
            id: idFrame,
            frameBorder: 0,
            width: 0,
            height: 0,
            css: 'display:none;visibility:hidden;height:0px',
            src: url
        });

    },

    isStatus: function(st){

    },

    downloadFile: function (args) {
        args = args || {};

        Ext.applyIf(args, {
            url: undefined,
            filename: 'arquivo.bin',  // Default filename
            approach: 'download',  // Acceptable values: 'download' and 'open'
        });

        if (!args.url) {
            throw new Error("downloadFile(): Missing required argument: 'url'");
        }

        if (args.approach === 'open') {
            window.open(url, '_blank');  // this triggers the browser's anti pop-up feature
        } else if (args.approach === 'download') {
            var anchor = document.createElement('a');
            anchor.href = args.url;
            anchor.download = args.filename;
            anchor.dispatchEvent(new MouseEvent('click'));
        }
    },

    /**
     * Após a implantação do novo Dashboard (e a nova posição do menu)
     * fez-se necessário redimensionar os componentes principais dos Managers.
     * A função seguinte faz o cálculo da largura do grid em relação ao tile.
     */
    updateGridAndTileDimensions: function (args) {
        args = args || {};

        Ext.applyIf(args, {
            target: undefined,  // Expected to be a GridPanel
            containerWidth: undefined,  // Expected to be a Manager
            tileWidth: 830,
            laptopBasicWidth: 1366,
            percentage: 45,  // Use 45% of the Manager width
        });

        var errorMsg = "updateGridAndTileDimensions(): Missing required argument: ";

        // Check required arguments
        if (!args.target) {
            throw new Error(errorMsg + "'target'");
        }

        if (!args.containerWidth) {
            throw new Error(errorMsg + "'containerWidth'");
        }

        // Do the calculations
        if (args.containerWidth <= args.laptopBasicWidth) {
            newWidth = args.containerWidth * args.percentage / 100;
        } else {
            newWidth = args.containerWidth - args.tileWidth;
        }

        // Set the new width
        args.target.setWidth(newWidth);
    },

    WindowNotificationOnTop: Ext.extend(
        Ext.Window,
        {
            updateCollection: function(collection) {
                Ext.each(
                    collection,
                    function(i) {
                        var flag = false;
                        Ext.each(this.collection, function(c) { flag = (c.pk == i.pk); return !flag; });
                        if(!flag) this.collection.push(i);
                    },
                    this
                );
            },

            constructor: function(cfg) {
                var cf = {
                    title: 'Sistema de notificações',
                    closable: true,
                    modal: true,
                    width: 700,
                    height: 400,
                    resizable: false,
                    draggable: false,
                    autoScroll: true,
                    buttons: [
                        {
                            text: 'Primeiro',
                            scope: this,
                            handler: function() {
                                this.activeItem = 0;
                                this.showItem();
                            }
                        },
                        {
                            text: 'Anterior',
                            scope: this,
                            handler: function() {
                                this.activeItem -= 1;
                                this.showItem();
                            }
                        },
                        {
                            text: 'Próximo',
                            scope: this,
                            handler: function() {
                                this.activeItem += 1;
                                this.showItem();
                            }
                        },
                        {
                            text: 'Ultimo',
                            scope: this,
                            handler: function() {
                                this.activeItem = (this.collection.length - 1);
                                this.showItem();
                            }
                        }
                    ]
                };

                Ext.apply(cf, cfg);

                toolkit.util.WindowNotificationOnTop.superclass.constructor.call(this, cf);
                this.collection = [];
                this.activeItem = 0;

                this.on(
                    'activate',
                    function() {
                        this.showItem();
                    },
                    this
                );
            },

            destroy: function() {
                var scope = this.scope ? this.scope : this;

                var ready = [];
                Ext.each(this.collection, function(i) { if(i.read) ready.push(i.pk); });

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('ENGNotification', 'read'),
                    params: {notif: ready},
                });

                this.callback.createDelegate(scope, [])();
                toolkit.util.WindowNotificationOnTop.superclass.destroy.call(this);
            },

            showItem: function() {
                var tpl = new Ext.XTemplate(
                    '<div class="message-container">',
                        '<div class="message-header">',
                            '<div><h2>{header_msg}</h2></div>',
                        '</div>',
                        '<div class="message-body">',
                            '<div>{msg}</div>',
                        '</div>',
                    '</div>'
                );

                if(this.activeItem < 0) this.activeItem = 0;
                if(this.activeItem >= this.collection.length) this.activeItem = this.collection.length - 1;

                var item = this.collection[this.activeItem];

                tpl.overwrite(this.body, item);
                this.setTitle('Mostrando a mensagem ' + (this.activeItem + 1) + ' de ' + this.collection.length);
                this.collection[this.activeItem].read = true;
            }
        }
    ),

    Notification: {
        notificationsData: false,
        toolTips: new Array(),

        startTaskToolTip: function(){
            Ext.TaskMgr.start({
                run: this.updateNotification,
                interval: 60 * 1000 //1 minutes
            });
        },

        tplToolTip: new Ext.XTemplate(
            '<tpl>',
                '<div style="width:438px; max-height:200px; display:block; overflow:auto;">',
                    '{msg}',  // use current array index to autonumber
                '</div>',
            '</tpl>',

            {
                // XTemplate configuration:
                compiled: true,
                disableFormats: true,
                // member functions:
                isInfo: function(type){
                    return type == 'INFO';
                },
                isError: function(type){
                    return type == 'ERROR';
                },
                isWarning: function(type){
                    return type == 'WARNING';
                }
            }

        ),

        createShortNotice: function(amount)
        {
            var message = 'Existe uma notificação não lida';
            if(amount > 1)
                message = 'Existem '+ amount +' notificações não lidas';

            var notice = new Ext.ToolTip({
                id: 'notice',
                closable: true,
                shadow: 'frame',
                shadowOffset: 7,
                showDelay: 7000,
                dismissDelay: 10000,
                hidden: true,
                autoHide: false,
                floating: true,
                data: {message:message},
                tpl: new Ext.XTemplate(
                    '<tpl>',
                        '<p id="notice-message" style="cursor:pointer; font-size:15px; font-weight:bold; color:#3366CC; padding:0 0 10px 10px;">',
                            '{message}',
                        '</p>',
                    '</tpl>'
                ),
                listeners: {
                    hide: function()
                    { this.destroy(); },
                    show: function()
                    {
                        var $this = this;
                        Ext.get('notice-message').on('click',
                            function()
                            {
                                //toolkit.util.Notification.showAllNotifications(false);
                                var button = Ext.getCmp('cmp-tooltip-notifications');
                                button.toggle(true);
                                $this.hide();
                            }
                        );

                    }
                }
            });

            notice.showAt([0, 0]);
            notice.getEl().alignTo(Ext.getBody(), 't-t', [0, 35]);
        },

        initToolTipNotification: function(notif){
            var ttnotif= new Ext.ToolTip({
                raw: notif,
                //draggable:true,
                title: '<b>'+notif.header_msg+'</b>',
                id: 'notif-tip-'+notif.pk,
                layout:'fit',
                shadow:'frame',
                shadowOffset: 7,
                floating: true,
                width: 450,
                autoScroll:true,
                data: notif,
                border:false,
                tpl: this.tplToolTip,
                autoHide: false,
                closable: true,
                viewed: false,
                type: notif.type_msg,
                el_left: null,
                el_rigth: null,
                pk: notif.pk,
                tools:[{
                    id:'close',//gear
                    qtip: 'Marcar como lida',
                    handler: function(event, toolEl, p){
                        this.readNotification(p);
                    },
                    scope: this
                }],
                listeners: {
                    render: function(p){
                        if(p.type=='WARNING')
                            p.header.setStyle('color','#0FF');
                    },
                    destroy: function(p){
                        var idx= this.indexOfTip(p.id);
                        if(idx>=0 && idx< this.toolTips.length) this.toolTips.splice(idx,1);
                        this.updateInfoNotification();
                    },
                    scope: this
                }
            });

            return ttnotif;
        },

        indexOfTip: function(id){
            if(this.toolTips && this.toolTips.length> 0){
                var total = this.toolTips.length;
                for(var x =0; x< total; x++){
                    if(this.toolTips[x].id== id) return x;
                }
                return -1;
            }
            return -1;
        },

        animeOnNew: function(){
            var btn = Ext.getCmp("cmp-tooltip-notifications");
            btn.btnEl.frame("FF0000", 3, {duration: 2});
        },

        clearToolsTips: function() {
            var ntips = [];

            Ext.each(
                this.toolTips,
                function(i) {
                    if(i.del === false) {
                        i.del = true;
                        ntips.push(i);
                    }
                },
                this
            );

            this.toolTips = ntips;
        },

        getNotificationSystem: function() {
            var notifications = [];

            Ext.each(
                this.toolTips,
                function(tip) {
                    if(tip.raw.media_type == 'SYS')
                        notifications.push(tip);
                }
            );

            return notifications;
        },

        getNotificationOntop: function() {
            var notifications = [];

            Ext.each(
                this.toolTips,
                function(tip) {
                    if(tip.raw.media_type == 'ONTOP')
                        notifications.push(tip.raw);
                }
            );

            return notifications;
        },

        updateInfoNotification: function(){
            // var txt = "Sem notificações";
            var btn= Ext.getCmp('cmp-tooltip-notifications');
            if(this.getNotificationSystem() && this.getNotificationSystem().length> 0){
                if(btn.disabled)
                    btn.enable();

                // _TODEL_ Foi removida a animação de square vermelho, pois a funcionalidade de Notificações foi transferida par ao novo Dashboard.
                //this.animeOnNew();

                // txt = '<div id="btn-notif" style="font-weight:bold;">(' + this.getNotificationSystem().length + ') Novas Notificações</div>'
            }else
                if(!btn.disabled){
                    btn.toggle(false);
                    btn.disable();
                }
            // btn.update(txt);

            if(this.getNotificationOntop().length > 0)
                this.createNotificationOnTop();
        },

        createNotificationOnTop: function() {
            if(!this.windowOntop)
                this.windowOntop = new toolkit.util.WindowNotificationOnTop({
                    callback: function() { this.windowOntop = null; },
                    scope: this
                });

            this.windowOntop.updateCollection(this.getNotificationOntop());
            this.windowOntop.show();
            this.windowOntop.showItem();
        },

        updateToolTipsNotification: function(result) {
            if (result) {
                var total = result.totalRows;
                var novo = false;

                // _TODEL_ Foi removido o ToolTip que exibi o total de notificações não lidas, pois a funcionalidade de Notificações foi transferida para ao novo Dashboard.
                // if(!Ext.getCmp('notice') && total > 0)
                //     this.createShortNotice(total);

                //TODO:Inserindo os TOOLTIPS das novas mensagens
                var me = this;
                result.result.forEach(function(item, index) {

                    idx = me.indexOfTip("notif-tip-"+item.pk);
                    if(idx >= 0)
                        me.toolTips[idx].del = false;
                    else {
                        tip = me.initToolTipNotification(item);
                        tip.del = false;
                        me.toolTips.push(tip);
                        novo = true;
                    }
                });

                //TODO:Apagando os TOOLSTIPS de mensagens antigas

                this.clearToolsTips();

                // _TODEL_ Foi removida a animação de square vermelho, pois a funcionalidade de Notificações foi transferida para ao novo Dashboard.
                //if(novo) this.animeOnNew();

                this.notificationsData= result;
            }
        },

        updateNotification: function(){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'RHServidor',
                    'get_notificacoes'
                ),
                method: 'GET',
                success: function(request) {
                    var result = Ext.decode(request.responseText);
                    toolkit.util.Notification.updateToolTipsNotification(result);
                    toolkit.util.Notification.updateInfoNotification();
                },
                failure: function() {
                    console.debug("Erro ao carregar notificações...");
                }
            });
        },

        reorderNotifications: function(tip){
            if(tip){
                var opt = {
                    duration: .2,
                    easing: 'elasticIn',
                    callback: function(){this.reorderNotifications(tip.el_rigth);},
                    scope: this
                };
                el= tip.getEl();
                el.alignTo(tip.el_left.getEl(),"tr-br",[0,0],opt);
            }
        },

        showNotification: function(notif){
            notif.showBy('cmp-tooltip-notifications');
        },

        // _TODEL_ Em razão do novo Dashboard, funcionalidade "Notificações" transferida
        showAllNotifications: function(only_news){
            var el_last= Ext.getCmp('cmp-tooltip-notifications');
            el_last.el_rigth = null;
            for(var x = 0; x < toolkit.util.Notification.toolTips.length; x++)
            {
                tip = toolkit.util.Notification.toolTips[x];
                if(!only_news||tip.viewed)
                {
                    tip.el_left = el_last;
                    //console.log(tip);
                    tip.showBy(tip.el_left.getEl(), 'tr-br');
                    tip.viewed = true;

                    if(el_last.el_rigth===null){
                        el_last.el_rigth= tip;
                    }

                    el_last = tip;
                }

            }
        },

        hideAllNotifications: function(only_news){
            for(var x=0; x< this.toolTips.length; x++){
                tip= this.toolTips[x];
                tip.hide();
                tip.el_left= null;
                tip.el_rigth= null;
            }
        },

        readNotification: function(tip){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'ENGNotification',
                    'read'
                ),
                params: {notif:tip.pk},
                success: function(request) {
                    var result = Ext.decode(request.responseText);
                    if(result.success){
                        tip.el_left.el_rigth= tip.el_rigth;
                        if(tip.el_rigth){
                            tip.el_rigth.el_left= tip.el_left;
                            this.reorderNotifications(tip.el_rigth);
                        }
                        tip.destroy();
                    }else{
                        Ext.MessageBox.show({
                           title: 'Erro ao marcar notificação como lida',
                           msg: result.error,
                           buttons: Ext.MessageBox.OK,
                           icon: Ext.MessageBox.ERROR
                        });
                    }
                },
                failure: function(request) {
                    if(request && request.result && request.result.error) {
                        Ext.MessageBox.show({
                           title: 'Erro de conexão',
                           msg: request.result.error,
                           buttons: Ext.MessageBox.OK,
                           icon: Ext.MessageBox.ERROR
                        });
                    }
                },
                scope: this
            });
        }
    },

    Tasks: {
        toolTips: new Array(),

        startTaskToolTip: function(){
            Ext.TaskMgr.start({
                run: this.verifyTasks,
                interval: 60 * 1000 //1 minutes
            });
        },

        animeOnNew: function(){
            var btn = Ext.getCmp('cmp-executions');
            if(!btn.pressed)
                btn.btnEl.frame("00FF00", 3, {duration: 2});
        },

        getBySid: function(sid){
            for(x = 0; x < this.toolTips.length; x++){
                if(this.toolTips[x].task.sid == sid){
                    return this.toolTips[x];
                    break;
                }
            }
            return null;
        },

        getSids: function(){
            var sids = [];
            toolkit.util.Tasks.toolTips.forEach(function(task){
                sids.push(task.sid);
            });
            return sids;
        },

        clearToolsTips: function() {
            var ntips = [];

            Ext.each(
                this.toolTips,
                function(i) {
                    if(i.del === false) {
                        i.del = true;
                        ntips.push(i);
                    }
                },
                this
            );

            this.toolTips = ntips;
        },

        updateToolTips: function(collection, updateToolTips){
            var sids = this.getSids();
            Ext.each(
                collection,
                function(task_){
                    var tip = this.getBySid(task_.sid);
                    if(!tip){
                        this.toolTips.push(new engine.TaskRunner({task: task_}));
                    }
                },
                this
            );
        },

        getTasksForUser: function(updateToolTips, callback){
            // console.debug(sid);
            var rest = new engine.TaskRunnerRestful();
            var cfg = {
                success: function(request) {
                    var result = Ext.decode(request.responseText);
                    this.updateToolTips(result.collection, updateToolTips);
                    if(callback && Ext.isFunction(callback))
                        callback();
                },
                failure: function(request) {
                    if(request && request.result && request.result.error) {
                        Ext.MessageBox.show({
                           title: 'Erro de conexão',
                           msg: request.result.error,
                           buttons: Ext.MessageBox.OK,
                           icon: Ext.MessageBox.ERROR
                        });
                    }
                },
                scope: this
            };

            Ext.apply(cfg, rest.getRoute('read'));

            Ext.Ajax.request(cfg);
        },

        showAllTasks: function(){
            var el_last = Ext.getCmp('cmp-executions');
            el_last.tip_bottom = null;
            Ext.each(
                this.toolTips,
                function(tip){
                    tip.tip_top = el_last;
                    //console.log(tip);
                    tip.showBy(tip.tip_top.getEl(), 'tr-br');
                    tip.viewed = true;

                    if(el_last.tip_bottom === null){
                        el_last.tip_bottom = tip;
                    }

                    el_last = tip;
                },
                this
            );
        },

        hideAllTasks: function(){
            Ext.each(
                this.toolTips,
                function(tip){
                    tip.hide();
                    tip.tip_top= null;
                    tip.tip_bottom= null;
                },
                this
            );
        },

        reorderTaskToolTips: function(tip){
            if(tip){
                var opt = {
                    duration: .2,
                    easing: 'elasticIn',
                    callback: function(){this.reorderTaskToolTips(tip.tip_bottom);},
                    scope: this
                };
                el= tip.getEl();
                el.alignTo(tip.tip_top.getEl(),"tr-br",[0,0],opt);
            }
        },

        closeTaskToolTip: function(tip){
            var manager = this;
            this.setVisualized(
                tip,
                function(){
                    tip.tip_top.tip_bottom = tip.tip_bottom;
                    if(tip.tip_bottom){
                        tip.tip_bottom.tip_top = tip.tip_top;
                        manager.reorderTaskToolTips(tip.tip_bottom);
                    }
                    manager.toolTips.remove(tip);
                    tip.destroy();
                }
            );
        },

        setVisualized: function(tip, callback){
            var rest = new engine.TaskRunnerRestful();
            var cfg = {
                params: {
                    visualized: true,
                },
                success: function(request) {
                    var result = Ext.decode(request.responseText);
                    console.debug('TaskToolTip '+ tip.task.sid+ ' visualized!');
                    if(callback){
                        callback();
                    }

                },
                failure: function() {
                    console.debug("Erro ao atualizar task para visualizada!");
                },
                scope: tip
            };

            Ext.apply(cfg, rest.getRoute('update', tip.task.pk));

            Ext.Ajax.request(cfg);
        },

        updateInfoTasks: function(){
            // var txt = "Sem notificações";
            var btn= Ext.getCmp('cmp-executions');
            if(this.toolTips.length > 0){
                btn.enable();
                this.animeOnNew();
            }else{
                btn.toggle(false);
                btn.disable();
            }
        },

        verifyTasks: function(){
            toolkit.util.Tasks.getTasksForUser(
                false,
                function(){
                    toolkit.util.Tasks.updateInfoTasks();
                }
            );
        }
    },

    Base64 : {

        base64s : "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",

        encode: function(decStr){
            if (typeof btoa === 'function') {
                 return btoa(decStr);
            }
            var base64s = this.base64s;
            var bits;
            var dual;
            var i = 0;
            var encOut = "";
            while(decStr.length >= i + 3){
                bits = (decStr.charCodeAt(i++) & 0xff) <<16 | (decStr.charCodeAt(i++) & 0xff) <<8 | decStr.charCodeAt(i++) & 0xff;
                encOut += base64s.charAt((bits & 0x00fc0000) >>18) + base64s.charAt((bits & 0x0003f000) >>12) + base64s.charAt((bits & 0x00000fc0) >> 6) + base64s.charAt((bits & 0x0000003f));
            }
            if(decStr.length -i > 0 && decStr.length -i < 3){
                dual = Boolean(decStr.length -i -1);
                bits = ((decStr.charCodeAt(i++) & 0xff) <<16) |    (dual ? (decStr.charCodeAt(i) & 0xff) <<8 : 0);
                encOut += base64s.charAt((bits & 0x00fc0000) >>18) + base64s.charAt((bits & 0x0003f000) >>12) + (dual ? base64s.charAt((bits & 0x00000fc0) >>6) : '=') + '=';
            }
            return(encOut);
        },

        decode: function(encStr){
            if (typeof atob === 'function') {
                return atob(encStr);
            }
            var base64s = this.base64s;
            var bits;
            var decOut = "";
            var i = 0;
            for(; i<encStr.length; i += 4){
                bits = (base64s.indexOf(encStr.charAt(i)) & 0xff) <<18 | (base64s.indexOf(encStr.charAt(i +1)) & 0xff) <<12 | (base64s.indexOf(encStr.charAt(i +2)) & 0xff) << 6 | base64s.indexOf(encStr.charAt(i +3)) & 0xff;
                decOut += String.fromCharCode((bits & 0xff0000) >>16, (bits & 0xff00) >>8, bits & 0xff);
            }
            if(encStr.charCodeAt(i -2) == 61){
                return(decOut.substring(0, decOut.length -2));
            }
            else if(encStr.charCodeAt(i -1) == 61){
                return(decOut.substring(0, decOut.length -1));
            }
            else {
                return(decOut);
            }
        }

    },

    /**
     * Objeto ScriptTab utiliazado para fazer scriptTag.
     */
    ScriptTag: {
        /**
         * Metodo estatico usado para fazer o parser em um XML procurando a tag Script
         * desta forma é feito o scriptTag em body.
         * @param xml: XMLObject com o xml a ser feito o parser.
         */
        parser_to_script: function(xml){
            try{
                var scriptCollection = xml.getElementsByTagName("script");
                if(scriptCollection != null) {
                    for(i in scriptCollection){
                        script = scriptCollection[i];
                        if(script.tagName == "script"){
                            sc = document.createElement("script");
                            sc.innerHTML = script.firstChild.nodeValue;
                            document.body.appendChild(sc);
                        }
                    }
                }
            }catch(e){
                alert("Ocorreu um erro em tempo de execução, no momento de converter ScriptTag!");
            }
        }
    },

    /**
     * Objeto manipulador da Prototype.
     */
    PrototypeManipulator: {
        /**
         * Metodo estatico utilizado para fazer copia de metodos entre modelos de objetos.
         * @param dst: Modelo de objeto de destino.
         * @param src: Modelo de objeto de origem.
         * @return Retorna o modelo de objeto destino com as modificações.
         */
        copy_method: function(dst, src) {
            for(var i in src.prototype)
                if(typeof(src.prototype[i]) == "function" && !dst.prototype[i])
                    dst.prototype[i] = src.prototype[i];

            return dst;
        },

        /**
         * Metodo estatico utilizado para fazer copia de atributos entre modelos de objetos.
         * @param dst: Modelo de objeto de destino.
         * @param src: Modelo de objeto de origem.
         * @return Retorna o modelo de objeto destino com as modificações.
         */
        copy_attribute: function(dst, src) {
            for(var i in src.prototype)
                if(typeof(src.prototype[i]) != "function" && !dst.prototype[i])
                    dst.prototype[i] = src.prototype[i];

            return dst;
        },

        /**
         * Metodo estatico utilizado para realizar herança entre modelos de objeto.
         * @param cls: Modelo de objeto de destino.
         * @param sp: Super class a ser herdado.
         * @return Retorna o modelo de objeto destino com as modificações.
         */
        extend: function(cls, sp) {
            cls = toolkit.util.PrototypeManipulator.copy_method(cls, sp);
            cls = toolkit.util.PrototypeManipulator.copy_attribute(cls, sp);

            return cls;
        }
    },

    /**
	 * Obejeto utilizado para manipular conexões AJAX.
	 */
    Ajax: {
        /**
         * Constroi um objeto de conexão AJAX.
         */
        factory_xhr: function() {
            var xhr;

            if (window.XMLHttpRequest) {
                xhr = new XMLHttpRequest();
            } else if (window.ActiveXObject) { // IE
                xhr = new ActiveXObject("Microsoft.XMLHTTP");
            }

            return xhr;
        },

        /**
         * Tipos de Metodos de consulta.
         */
        METHOD_TYPE: {
            POST: 'POST',
            GET: 'GET'
        },

        /**
         * Realza uma requisição a uma URL tendo com retorno um JSON.
         * @param method: Metodo a ser utilizado na consulta.
         * @param url: URL utilizada para requisições.
         * @param args: Array de argumentos a serem passados para requisição.
         * @return Em caso de sucesso será devoldo o objeto JSON válido gerado pelo serevidor
         * caso contrário será devolvido um JSON limpo.
         */
        request_json: function(method, url, args) {

            var obj;
            var code;

            var waiting = new toolkit.plugins.WindowLoading();
            var flag = false;

            setTimeout(function() {
                    if(!flag) {
                        flag = true;
                        waiting.show();
                    }
                },
                100
            );

            if(method == toolkit.util.Ajax.METHOD_TYPE.POST) {
                try {
                    code = "obj = " + toolkit.util.Ajax.request_text_post(url, args);
                    eval(code);
                }
                catch(e) {
                    obj = {
                        exception: "toolkit.exception.JSONError",
                        messageException: "Ocorreu um erro tratando o retorno do servidor.<br/>Algum erro ocorreu durante o processo de construção da informação no servidor.<br/>"
                    };

                    console.debug("toolkit.exception.JSONError");
                }
            }
            else if(method == toolkit.util.Ajax.METHOD_TYPE.GET){
                try {
                    code = "obj = " + toolkit.util.Ajax.request_text_get(url, args);
                    eval(code);
                }
                catch(e) {
                    obj = {
                        exception: "toolkit.exception.JSONError",
                        messageException: "Ocorreu um erro tratando o retorno do servidor.<br/>Algum erro ocorreu durante o processo de construção da informação no servidor."
                    };

                    console.debug("toolkit.exception.JSONError");
                    console.debug(code);
                }
            }

            if(obj.exception != undefined) {
                var e;

                try {
                    var src = ("e = new " + obj.exception + "('" + obj.messageException + "')");
                    eval(src);
                    e.display();
                }
                catch(e) {
                    console.debug(e);
                }
            }

            setTimeout(function() {
                    if(flag) {
                        flag = true;
                        waiting.destroy();
                    }
                },
                1000
            );

            return obj;
        },

        /**
         * Realza uma requisição a uma URL tendo com retorno um XML.
         * @param method: Metodo a ser utilizado na consulta.
         * @param url: URL utilizada para requisições.
         * @param args: Array de argumentos a serem passados para requisição.
         * @param callback: Função utilizada para tratar o retorno, caso seja omitido o metodo será tratado com syncorno.
         * @return Em caso de sucesso será devoldo o objeto XML válido gerado pelo serevidor
         * caso contrário será devolvido um XML limpo.
         */
        request_xml: function(method, url, args, callback) {
            if(method == toolkit.util.Ajax.METHOD_TYPE.POST)
                return toolkit.util.Ajax.request_xml_post(url, args, callback);
            else if(method == toolkit.util.Ajax.METHOD_TYPE.GET)
                return toolkit.util.Ajax.request_xml_get(url, args, callback);
        },

        /**
         * Realza uma requisição a uma URL.
         * @param method: Metodo a ser utilizado na consulta.
         * @param url: URL utilizada para requisições.
         * @param args: Array de argumentos a serem passados para requisição.
         * @param callback: Função utilizada para tratar o retorno, caso seja omitido o metodo será tratado com syncorno.
         * @return Retorna uma String.
         */
        request_text: function(method, url, args, callback) {
            if(method == toolkit.util.Ajax.METHOD_TYPE.POST)
                return toolkit.util.Ajax.request_text_post(url, args, callback);
            else if(method == toolkit.util.Ajax.METHOD_TYPE.GET)
                return toolkit.util.Ajax.request_text_get(url, args, callback);
        },

        /**
         * Realza uma requisição a uma URL usando o metodo POST tendo como retorno um XML.
         * @param method: Metodo a ser utilizado na consulta.
         * @param url: URL utilizada para requisições.
         * @param args: Array de argumentos a serem passados para requisição.
         * @param callback: Função utilizada para tratar o retorno, caso seja omitido o metodo será tratado com syncorno.
         * @return Em caso de sucesso será devoldo o objeto XML válido gerado pelo serevidor
         * caso contrário será devolvido um XML limpo.
         */
        request_xml_post: function(url, args, callback) {

            var xhr = toolkit.util.Ajax.factory_xhr();

            if(callback == undefined || callback == false) {
                xhr.open('POST', url, false);
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                if(typeof(args) == "string")
                    xhr.send(args);
                else
                    xhr.send(toolkit.util.QueryBuild.build(args));

                return xhr.responseXML;
            }
            else {
                xhr.onreadystatechange = callback;
                xhr.open(POST, url);
                if(typeof(args) == "string")
                    xhr.send(args);
                else
                    xhr.send(toolkit.util.QueryBuild.build(args));
            }

        },

        /**
         * Realza uma requisição a uma URL usando o metodo GET tendo como retorno um XML.
         * @param method: Metodo a ser utilizado na consulta.
         * @param url: URL utilizada para requisições.
         * @param args: Array de argumentos a serem passados para requisição.
         * @param callback: Função utilizada para tratar o retorno, caso seja omitido o metodo será tratado com syncorno.
         * @return Em caso de sucesso será devoldo o objeto XML válido gerado pelo serevidor
         * caso contrário será devolvido um XML limpo.
         */
        request_xml_get: function(url, args, callback) {

            var xhr = toolkit.util.Ajax.factory_xhr();

            if(callback == undefined || callback == false) {
                xhr.open('GET', url, false);
                if(typeof(args) == "string")
                    xhr.send(args);
                else
                    xhr.send(toolkit.util.QueryBuild.build(args));

                return xhr.responseXML;

            }
            else {
                xhr.onreadystatechange = callback;
                xhr.open(GET, url);
                if(typeof(args) == "string")
                    xhr.send(args);
                else
                    xhr.send(toolkit.util.QueryBuild.build(args));

            }
        },

        /**
         * Realza uma requisição a uma URL usando o metodo POST.
         * @param method: Metodo a ser utilizado na consulta.
         * @param url: URL utilizada para requisições.
         * @param args: Array de argumentos a serem passados para requisição.
         * @param callback: Função utilizada para tratar o retorno, caso seja omitido o metodo será tratado com syncorno.
         * @return Retorna uma String.
         */
        request_text_post: function(url, args, callback) {

            var xhr = toolkit.util.Ajax.factory_xhr();

            if(callback == undefined || callback == false) {
                xhr.open('POST', url, false);
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                if(typeof(args) == "string")
                    xhr.send(args);
                else
                    xhr.send(toolkit.util.QueryBuild.build(args));

                return xhr.responseText;
            }
            else {
                xhr.onreadystatechange = callback;
                xhr.open(POST, url);
                if(typeof(args) == "string")
                    xhr.send(args);
                else
                    xhr.send(toolkit.util.QueryBuild.build(args));
            }

        },

        /**
         * Realza uma requisição a uma URL usando o metodo GET.
         * @param method: Metodo a ser utilizado na consulta.
         * @param url: URL utilizada para requisições.
         * @param args: Array de argumentos a serem passados para requisição.
         * @param callback: Função utilizada para tratar o retorno, caso seja omitido o metodo será tratado com syncorno.
         * @return Retorna uma String.
         */
        request_text_get: function(url, args, callback) {

            var xhr = toolkit.util.Ajax.factory_xhr();

            if(callback == undefined || callback == false) {
                xhr.open('GET', url, false);
                if(typeof(args) == "string")
                    xhr.send(args);
                else
                    xhr.send(toolkit.util.QueryBuild.build(args));

                return xhr.responseText;

            }
            else {
                xhr.onreadystatechange = callback;
                xhr.open(GET, url);
                if(typeof(args) == "string")
                    xhr.send(args);
                else
                    xhr.send(toolkit.util.QueryBuild.build(args));

            }
        }
    },

    /**
     * Utilizado para aplicar normalização na camada JavaScript.
     */
    Normalize: {
        /**
         * Metodo estatico utilizado para construir uma url para chamada de um metodo em um Controller.
         * @param controller: Nome do controller.
         * @param action: Nome da action.
         * @param args: Lista de argumentos.
         * @return Será retorna uma String com o contúdo /controller/action/arg1/.../argN/
         */
        controller_action: function(controller, action, args) {
            var src = "/" + global.Context + "/";

            if(controller != null && action != null) {
                src += controller + "/" + action + "/";

                if(args != null)
                    for(var i = 0; i <  args.length; i++)
                        src += args[i] + "/";
            }
            else if(controller != null)
                src += controller + "/";

            return src;
        }
    },

    /**
	 * Utilizado para gerar QueryString para requisições Ajax.
	 */
    QueryBuild: {

        /**
         * Metodo utilizado para detectar o tipo de um objeto.
         * @param obj: Objeto utilizado para detecção.
         * @return Retorna o tipo do objeto.
         */
        detectType: function(obj) {
            if(typeof(obj) == "object") {
                if(obj instanceof Array)
                    return "array";
                else
                    return "object";
            }
            else return typeof(obj);
        },

        /**
         * Constroi uma QueryString de acordo com obj.
         * @param obj: Fonte de dados para QueryString
         * @return Retorna uma QueryString tratada pronta para ser utilizada.
         */
        build : function(obj) {
            var type = toolkit.util.QueryBuild.detectType(obj);

            switch(type) {
                case "array":
                    return toolkit.util.QueryBuild._from_array(obj);
                    break;
                case "object":
                    return toolkit.util.QueryBuild._from_json(obj);
                    break;
                default:
                    return obj;
            }
        },

        /**
         * Constroi uma QueryString a partir de uma Array.
         * @param obj: Array fonte de dados para QueryString
         * @return Retorna uma QueryString tratada pronta para ser utilizada.
         */
        _from_array: function(arrays) {
            var q = "";
            var item = undefined;

            if (arrays != undefined) {
                for (i in arrays) {
                    item = arrays[i];
                    q += (i > 0 ? "&" : "");
                    q += encodeURI(item[0]) + "=" + (encodeURI(item[1]));
                }
            }
            return q;
        },

        /**
         * Constroi uma QueryString a partir de uma JSON.
         * @param obj: JSON fonte de dados para QueryString
         * @return Retorna uma QueryString tratada pronta para ser utilizada.
         */
        _from_json: function(json) {return Ext.urlEncode(json);}
    }
};
