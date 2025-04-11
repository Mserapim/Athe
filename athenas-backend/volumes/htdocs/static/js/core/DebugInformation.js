
/**
 *
 **/
Ext._define('core.DebugInformation', {
    extend: 'Object',

    statics: {

        toogle: function() {
            if(core.DebugInformation._state === 0) {
                core.DebugInformation._button.getEl().move(
                    'left', 350, {
                        delay: 500
                    }
                );
                core.DebugInformation._panel.getEl().move(
                    'left', 350, {
                        delay: 500
                    }
                );

                core.DebugInformation._state = 1;
            }
            else {
                core.DebugInformation._button.getEl().move(
                    'right', 350, {
                        delay: 500
                    }
                );
                core.DebugInformation._panel.getEl().move(
                    'right', 350, {
                        delay: 500
                    }
                );

                core.DebugInformation._state = 0;
            }
        },

        renderData: function(data) {
            var tpl = Ext._create('Ext.XTemplate', [
                '<div class="panel-info-body">',
                    '<tpl for="sections">',
                    '<div class="section">',
                        '<h2>{title}</h2>',
                        '<tpl for="collection">',
                            '<div class="label">{name}:</div>',
                            '<div class="value">{value}</div>',
                        '</tpl>',
                    '</div>',
                    '</tpl>',
                '</div>'
            ]);

            tpl.overwrite(
                core.DebugInformation._panel.getEl(),
                data
            );
        },

        renderTab: function() {
            core.DebugInformation._button = Ext._create('Ext.Container', {
                autoEl: 'div',
                width: 32,
                height: 48,
                renderTo: Ext.getBody(),
                cls: 'debug-info-button'
            });

            core.DebugInformation._panel = Ext._create('Ext.Container', {
                autoEl: 'div',
                width: 350,
                renderTo: Ext.getBody(),
                cls: 'debug-info-panel'
            });


            core.DebugInformation._button.getEl().on({
                click: function() {
                    core.DebugInformation.toogle();
                }
            });

            core.DebugInformation._button.render();
            core.DebugInformation._panel.render();

            core.DebugInformation._state = 1;
            setTimeout(
                function() {
                    core.DebugInformation.toogle();
                },
                3000
            );

            var task;
            task = Ext.TaskMgr.start({
                interval: 15000,
                run: function() {
                    Ext.Ajax.request({
                        url: core.callAction('DebugInformation', 'data'),
                        success: function(xhr) {
                            var rst = Ext.decode(xhr.responseText);
                            if(rst.success) core.DebugInformation.renderData(rst);
                        },
                        failure: function() {
                            Ext.TaskMgr.stop(task);
                            console.info('Debug task foi interrompida.');
                        }
                    });
                }
            });
        },

        start: function() {
            Ext.Ajax.request({
                url: core.callAction('DebugInformation', 'data'),
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);
                    if (rst.success && !(localStorage.getItem('hideDebugInfo') === 'on')) {
                        core.DebugInformation.renderTab();
                    };
                }
            });
        }
    }
});
